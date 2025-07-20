# BluedBot

> A powerful client panel for [Pelican Panel](https://github.com/pelican-dev/panel), all in a Discord bot.

**BluedBot** is a Discord bot built with usability in mind. It acts as a client panel for Pelican Panel, using Python for flexibility and performance.

---

## 🌟 Features

### 🧱 Resource System
- Built-in default resources
- Support for custom/additional resources

### 💰 Coins System
- Linkvertise integration *(optional, reverse proxy required — see below)*
- Coin gifting between users
- Shop to buy additional resources

### 🔁 Renewal System
- Automatic resource/server renewal checks
- Uses coins to renew server allocations

### 🖥️ Server Management
- Create new servers
- View server information
- Edit server details
- Delete servers

### 👤 Account System
- Create and manage user accounts
- View account details

### 🛠️ Admin/Moderation
- Blacklist users from using the bot *(requires registration)*
- Add coins/resources to users

### ⚙️ Node & Egg System
- Easily add/edit node and egg configurations
- Set specific limits for each item

---

## 🐛 Bug Reports & Support

- 💬 [Join our Discord server](https://discord.gg/SdyRkZ5HQM) for support and community chat  
- 🐞 [Post an issue](https://github.com/bluekyeet/BluedBot/issues) if you encounter bugs

---

## 🚀 Installation

> **Requires Python 3.12**

1. Clone the repository and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy the environment file and configure it:

   ```bash
   cp .example.env .env
   ```

3. Edit `.env` and update the `nodes/` and `eggs/` folders with your configurations.

---

### ⚠️ Linkvertise Integration Note

If you plan to use Linkvertise, **you must configure a reverse proxy** using NGINX (or another web server) to the port specified in the `.env` file.

---

Made with 💙 by [@bluekyeet](https://github.com/bluekyeet)
