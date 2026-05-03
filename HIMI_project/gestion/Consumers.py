import json
from channels.generic.websocket import AsyncWebsocketConsumer


class VoIPConsumer(AsyncWebsocketConsumer):
    """
    Serveur de signalisation WebRTC pour les appels VoIP.
    Chaque paire d'utilisateurs partage un "room" unique.
    Les messages SDP (offer/answer) et ICE candidates
    sont relayés entre les deux pairs via ce consumer.
    """

    async def connect(self):
        self.user = self.scope["user"]

        # Refuser les connexions non authentifiées
        if not self.user.is_authenticated:
            await self.close()
            return

        # Récupérer l'ID de l'interlocuteur depuis l'URL
        self.contact_id = self.scope["url_route"]["kwargs"]["contact_id"]

        # Créer un nom de room unique et symétrique :
        # min(id_a, id_b)_max(id_a, id_b) → même room dans les deux sens
        ids = sorted([self.user.id, int(self.contact_id)])
        self.room_name = f"voip_{ids[0]}_{ids[1]}"

        # Rejoindre le groupe Channel
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "room_name"):
            # Informer l'autre utilisateur que la connexion est fermée
            await self.channel_layer.group_send(
                self.room_name,
                {
                    "type": "voip_signal",
                    "message": {"type": "peer_disconnected"},
                    "sender_channel": self.channel_name,
                },
            )
            await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        """
        Reçoit un message WebSocket du navigateur et le relaie
        à l'autre utilisateur dans la même room.
        Types de messages acceptés :
          - offer      : offre SDP de l'appelant
          - answer     : réponse SDP de l'appelé
          - ice-candidate : candidat ICE
          - call-request  : demande d'appel entrant
          - call-rejected : appel refusé
          - call-ended    : appel terminé
        """
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        # Relayer le message à tous les membres du groupe
        # sauf l'expéditeur lui-même
        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "voip_signal",
                "message": data,
                "sender_channel": self.channel_name,
                "sender_name": self.user.get_full_name() or self.user.username,
            },
        )

    async def voip_signal(self, event):
        """
        Handler appelé quand un message est envoyé au groupe.
        On ne renvoie pas le message à l'expéditeur original.
        """
        if event.get("sender_channel") == self.channel_name:
            return  # Ne pas renvoyer à soi-même

        await self.send(
            text_data=json.dumps(
                {
                    **event["message"],
                    "sender_name": event.get("sender_name", ""),
                }
            )
        )