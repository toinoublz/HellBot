from DB import DB

db = DB("hellbot")

# Configuration du salon de logs normal
db.add('logs_channel_id', 1306683155260117133)

# Configuration du salon des super logs (pour les erreurs)
db.add('super_logs_channel_id', 1306683155260117133)  # Remplacez par l'ID du canal souhaité
