class AdminPage:
    def __init__(self, bot):
        self.admins = [82755431]
        self.bot = bot
    
    def add_admin(self, id):
        self.admins.append(id)

    def notify_one(self, msg):
        self.bot.sendMessage(admin_list[0], msg)

    def notify_all(self, msg):
        for admin_id in admins:
            self.bot.sendMessage(admin_id, msg)

    def is_admin(self, id):
        return id in self.admins
