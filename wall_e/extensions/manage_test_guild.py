import asyncio

from discord.ext import commands
from discord.ext.commands import Context

from utilities.global_vars import wall_e_config, bot

from utilities.file_uploading import start_file_uploading
from utilities.setup_logger import Loggers


class ManageTestGuild(commands.Cog):

    def __init__(self):
        log_info = Loggers.get_logger(logger_name="ManageTestGuild")
        self.logger = log_info[0]
        self.debug_log_file_absolute_path = log_info[1]
        self.warn_log_file_absolute_path = log_info[2]
        self.error_log_file_absolute_path = log_info[3]
        self.logger.info("[ManageTestGuild __init__()] initializing ManageTestGuild")
        bot.add_check(ManageTestGuild.check_text_command_test_environment)
        self.guild = None

    @commands.Cog.listener(name="on_ready")
    async def get_guild(self):
        self.guild = bot.guilds[0]

    @commands.Cog.listener(name="on_ready")
    async def upload_debug_logs(self):
        if wall_e_config.get_config_value('basic_config', 'ENVIRONMENT') != 'TEST':
            while self.guild is None:
                await asyncio.sleep(2)
            await start_file_uploading(
                self.logger, self.guild, bot, wall_e_config, self.debug_log_file_absolute_path,
                "manage_test_guild_debug"
            )

    @commands.Cog.listener(name="on_ready")
    async def upload_warn_logs(self):
        if wall_e_config.get_config_value('basic_config', 'ENVIRONMENT') != 'TEST':
            while self.guild is None:
                await asyncio.sleep(2)
            await start_file_uploading(
                self.logger, self.guild, bot, wall_e_config, self.warn_log_file_absolute_path,
                "manage_test_guild_warn"
            )

    @commands.Cog.listener(name="on_ready")
    async def upload_error_logs(self):
        if wall_e_config.get_config_value('basic_config', 'ENVIRONMENT') != 'TEST':
            while self.guild is None:
                await asyncio.sleep(2)
            await start_file_uploading(
                self.logger, self.guild, bot, wall_e_config, self.error_log_file_absolute_path,
                "manage_test_guild_error"
            )

    @commands.Cog.listener(name="on_ready")
    async def create_main_channel(self):
        """
        this command is used by the TEST guild to create the channel from which this TEST container
         will process commands
        :return:
        """
        while self.guild is None:
            await asyncio.sleep(2)
        self.logger.info(
            "[ManageTestGuild create_main_channel()] creating text channel for bot commands in TEST guild."
        )
        await bot.bot_channel_manager.create_or_get_channel_id(
            self.logger, self.guild, wall_e_config.get_config_value('basic_config', 'ENVIRONMENT'),
            "general_channel"
        )
        self.logger.debug(
            "[ManageTestGuild create_main_channel()] text channel for bot commands in TEST guild created."
        )

    @commands.command(brief="returns which branch the user is testing")
    @commands.has_role("Bot_manager")
    async def debuginfo(self, ctx):
        self.logger.info(f"[ManageTestGuild debuginfo()] debuginfo command detected from {ctx.message.author}")
        await ctx.send(
            '```You are testing the latest commit of branch or pull request: '
            f'{wall_e_config.get_config_value("basic_config", "BRANCH_NAME")}```',
            reference=ctx.message
        )

    @classmethod
    def check_text_command_test_environment(cls, ctx: Context):
        """
        this check is used by the TEST guild to ensure that each TEST container will only process incoming
         text commands that originate from channels that match the name of their branch
        :param ctx: the ctx object that is part of command parameters that are not slash commands
        :return:
        """
        guild = ctx.message.guild
        channel_name = None if guild is None else ctx.channel.name
        if wall_e_config.get_config_value('basic_config', 'ENVIRONMENT') != 'TEST':
            return True
        branch_name = wall_e_config.get_config_value('basic_config', 'BRANCH_NAME').lower()
        if guild is None and branch_name == "master":
            return True
        text_bot_channel_name = f"{branch_name}_bot_channel"
        correct_test_guild_text_channel = (
            guild is not None and (channel_name == text_bot_channel_name or channel_name == branch_name)
        )
        return correct_test_guild_text_channel


async def setup(bot):
    await bot.add_cog(ManageTestGuild())
