"""
Server Setup Cog — In-Game Registration
Allows server owners/admins to register their server directly via Discord.
"""
import discord
from discord import app_commands
from discord.ext import commands
import logging
import os

logger = logging.getLogger(__name__)

BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID", "0"))

class RegistrationModal(discord.ui.Modal, title="Server Registration Setup"):
    alliance_name = discord.ui.TextInput(
        label="Alliance Name",
        placeholder="e.g. Dragon Knights",
        min_length=2,
        max_length=100,
        required=True
    )

    access_code = discord.ui.TextInput(
        label="Access Code (Password)",
        placeholder="Choose a secret code for dashboard access...",
        style=discord.TextStyle.short,
        min_length=4,
        max_length=64,
        required=True
    )

    def __init__(self):
        super().__init__()

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            from db.mongo_adapters import PendingConfigAdapter, ServerAllianceAdapter, mongo_enabled
            if not mongo_enabled():
                await interaction.followup.send("❌ Database not available.", ephemeral=True)
                return

            guild_id = interaction.guild_id
            user_id = interaction.user.id
            username = interaction.user.name

            # Check if user already has a registration
            existing_user = await PendingConfigAdapter.get_by_user_async(user_id)
            if existing_user and existing_user.get("guild_id") != str(guild_id):
                await interaction.followup.send(
                    f"⚠️ You already have a registration on server `{existing_user.get('guild_name', 'another server')}`. "
                    "Only one registration per user is allowed.",
                    ephemeral=True
                )
                return

            # Submit the request
            ok = await PendingConfigAdapter.submit_async(
                guild_id=guild_id,
                guild_name=interaction.guild.name,
                alliance_name=self.alliance_name.value.strip(),
                access_code=self.access_code.value.strip(),
                discord_user_id=user_id,
                discord_username=username,
            )

            if not ok:
                await interaction.followup.send("❌ Failed to save registration request. Try again later.", ephemeral=True)
                return

            # Notify global admin
            try:
                if BOT_OWNER_ID:
                    admin_user = await interaction.client.fetch_user(BOT_OWNER_ID)
                    if admin_user:
                        msg = (
                            f"📋 **New Server Registration Request (Via Bot)**\n\n"
                            f"**Server:** {interaction.guild.name} (`{guild_id}`)\n"
                            f"**Alliance Name:** `{self.alliance_name.value.strip()}`\n"
                            f"**Requested by:** {username} (`{user_id}`)\n"
                            f"**Access Code:** ||`{self.access_code.value.strip()}`||\n\n"
                            f"Reply with `/reg-approve {guild_id}` or `/reg-deny {guild_id}`"
                        )
                        await admin_user.send(msg)
            except Exception as e:
                logger.warning(f"Could not DM admin: {e}")

            await interaction.followup.send(
                "✅ **Registration Submitted!**\n\n"
                "Your request has been sent to the global administrator for review.\n"
                "You will receive a Direct Message once it is approved.",
                ephemeral=True
            )

        except Exception as e:
            logger.error(f"Error in registration modal: {e}")
            await interaction.followup.send("❌ An unexpected error occurred.", ephemeral=True)


class ServerSetup(commands.Cog):
    """In-game server setup and registration."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="setup",
        description="Register this server and set an access code for the web dashboard."
    )
    @app_commands.default_permissions(administrator=True)
    async def setup_command(self, interaction: discord.Interaction):
        try:
            from db.mongo_adapters import PendingConfigAdapter, ServerAllianceAdapter, mongo_enabled
            if not mongo_enabled():
                await interaction.response.send_message("❌ Database not available.", ephemeral=True)
                return

            # Check if already approved
            existing_guild = await PendingConfigAdapter.get_by_guild_async(interaction.guild_id)
            if existing_guild and existing_guild.get("status") == "approved":
                await interaction.response.send_message(
                    "✅ This server is already configured and approved. Use `/manage` to access the dashboard.",
                    ephemeral=True
                )
                return
            
            if existing_guild and existing_guild.get("status") == "pending":
                await interaction.response.send_message(
                    "⏳ A registration request for this server is already **pending**. "
                    "You will receive a DM when the admin reviews it.",
                    ephemeral=True
                )
                return

            # Check user restrictions
            existing_user = await PendingConfigAdapter.get_by_user_async(interaction.user.id)
            if existing_user and existing_user.get("guild_id") != str(interaction.guild_id):
                await interaction.response.send_message(
                    f"⚠️ You already have a registration on server `{existing_user.get('guild_name', 'another server')}`. "
                    "Only one registration per user is allowed.",
                    ephemeral=True
                )
                return

            # Open Modal
            await interaction.response.send_modal(RegistrationModal())

        except Exception as e:
            logger.error(f"Error in /setup command: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message("❌ An error occurred.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ServerSetup(bot))
    logger.info("✅ ServerSetup cog loaded")
