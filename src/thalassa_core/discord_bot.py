import discord
from discord.ext import commands, tasks
import logging
from dotenv import load_dotenv
import os
import asyncio
from datetime import datetime, timedelta, timezone
import re
import platform
import subprocess

load_dotenv()

class CIDiscordBot:
    def __init__(self):
        
        # CI TIME channels
        # self.SCOUTED_CHANNEL_ID = 705304365061373973
        # self.ARCHIVE_CHANNEL_ID = 1445931935204638791
        # self.MAP_TRADING_CHANNEL_ID = 592238131978174475

        self.load_discord_token()
        self.loop = None 

        # Test Server channels
        self.SCOUTED_CHANNEL_ID = 1419043075715498129
        self.ARCHIVE_CHANNEL_ID = 1445936225687961801
        self.MAP_TRADING_CHANNEL_ID = 1445958912837943467

        # Logging setup
        handler = logging.FileHandler(filename='src/media/discord.log', encoding='utf-8', mode='a')
        logging.basicConfig(
            level=logging.INFO,
            handlers=[handler],
            format="%(asctime)s %(levelname)s %(message)s"
        )

        # Discord bot setup
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        self.bot = commands.Bot(command_prefix="!", intents=intents)

        self.delete_after_days = 10

        # Bind events
        self.bot.event(self.on_ready)
    
    def run_bot_threaded(self):
        """Run this method inside the separate thread."""
        if not self.load_discord_token():
            logging.warning("No Token found")
            return
        
        # This blocks the THREAD, not the GUI
        self.bot.run(self.token, log_handler=None, log_level=logging.INFO)

    async def safe_delete_message(self, message, reason=""):
        """Delete a message safely with logging."""
        try:
            # Archive message before deletion
            await self.archive_message(message)
            await message.delete()
            logging.info(f"Deleted message {message.id} from {message.author.display_name} {reason}")
            await asyncio.sleep(1)  # Avoid rate limits
        except discord.Forbidden:
            logging.error("Missing permission to delete messages.")
        except discord.HTTPException as e:
            logging.error(f"Failed to delete message: {e}")

    async def archive_message(self, message):
        """Send a copy of the message and its attachments to the archive channel."""
        archive_channel = self.bot.get_channel(self.ARCHIVE_CHANNEL_ID)
        if archive_channel is None:
            logging.warning("Archive channel not found!")
            return

        content = f"**{message.author.display_name}** on {message.created_at.date()}\n\n{message.content}"
        files = [await att.to_file() for att in message.attachments]

        try:
            await archive_channel.send(content, files=files)
            logging.info(f"Archived message {message.id} from {message.author.display_name}")
        except discord.HTTPException as e:
            logging.error(f"Failed to archive message {message.id}: {e}")

    async def check_old_messages(self):
        """Check and delete old messages in the scouted channel."""
        channel = self.bot.get_channel(self.SCOUTED_CHANNEL_ID)
        if channel is None:
            logging.info("Scouted channel not found!")
            return

        default_cutoff_time = datetime.now(timezone.utc) - timedelta(days=self.delete_after_days)

        async for message in channel.history(limit=None, oldest_first=True):
            has_attachment = any(
                att.content_type and att.content_type.startswith("image/")
                for att in message.attachments
            )

            # Check for decay day in message content
            match = re.search(r'(^| |,|-)([0-8])([Dd])( |$|-|,)', message.content)
            if match:
                decay_day = int(match.group(2))
                cutoff_time = datetime.now(timezone.utc) - (timedelta(days=decay_day) + timedelta(days=1))
            else:
                cutoff_time = default_cutoff_time

            if not has_attachment:
                await self.safe_delete_message(message, "(no image)")
            elif message.created_at < cutoff_time:
                await self.safe_delete_message(message, "(map dusted)")

    async def on_ready(self):
        logging.info(f"{self.bot.user} is online.")
        # We capture the loop here to be safe
        self.loop = asyncio.get_running_loop()
        
        await self.check_old_messages()
        logging.info(f"Sweep complete. Bot is ready for commands.")

    async def new_trade_message(self, message: str):
        """The actual async function that sends the message."""
        channel = self.bot.get_channel(self.MAP_TRADING_CHANNEL_ID)
        if channel is None:
            logging.warning("Trade channel not found!")
            return
        try:
            await channel.send(content=message)
            logging.info(f"Sent trade message: {message}")
        except Exception as e:
            logging.error(f"Failed to send trade message: {e}")

    def run_sweep(self):
        if not self.token:
            logging.warning("No DISCORD_TOKEN found in environment variables.")
            return
        self.bot.run(self.token, log_handler=None, log_level=logging.INFO)

    def send_trade_from_external(self, message: str):
        """
        THREAD-SAFE BRIDGE: Call this from your GUI (Tkinter).
        It schedules the async task on the bot's event loop.
        """
        if self.bot.is_ready() and self.loop:
            asyncio.run_coroutine_threadsafe(self.new_trade_message(message), self.loop)
        else:
            logging.warning("Bot is not ready yet; cannot send message.")

    def set_discord_token(self, token: str) -> None:
        """Store a Discord token at the system level."""
        self.token = token
        os.environ["DISCORD_TOKEN"] = token  # current session

        system = platform.system()

        try:
            if system == "Windows":
                # setx stores it permanently for the current user
                subprocess.run(["setx", "DISCORD_TOKEN", token], check=True)
            elif system in ("Linux", "Darwin"):  # Darwin = macOS
                # append to user's shell profile (~/.bashrc, ~/.zshrc)
                shell = os.environ.get("SHELL", "")
                profile_file = ""
                if "bash" in shell:
                    profile_file = os.path.expanduser("~/.bashrc")
                elif "zsh" in shell:
                    profile_file = os.path.expanduser("~/.zshrc")
                else:
                    profile_file = os.path.expanduser("~/.profile")

                # Avoid duplicate entries
                with open(profile_file, "a+") as f:
                    f.seek(0)
                    lines = f.readlines()
                    if not any("DISCORD_TOKEN=" in line for line in lines):
                        f.write(f'\nexport DISCORD_TOKEN="{token}"\n')

            logging.info("Discord token stored at system level.")
        except Exception as e:
            logging.error(f"Failed to persist token at system level: {e}")

    def load_discord_token(self):
        """Load the Discord token from environment variables."""
        self.token = os.getenv("DISCORD_TOKEN")
        if not self.token:
            logging.warning("No DISCORD_TOKEN found in environment variables.")
        return self.token
    

if __name__ == "__main__":
    ci_discord_bot = CIDiscordBot()
    ci_discord_bot.run_sweep()
