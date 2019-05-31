import json
from functools import partial
import discord
from discord.ext import commands, tasks

prefix = '> '


class StrDict(dict):
    def __setitem__(self, k, v):
        return super().__setitem__(str(k), v)

    def __getitem__(self, k):
        return super().__getitem__(str(k))

    def __contains__(self, v):
        return super().__contains__(str(v))


class PrivateChannels(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        try:
            with open('private_channels_cfg.json') as f:
                self.data = json.load(f)
        except json.JSONDecodeError:
            self.data = {}
        self.data = StrDict(self.data)
        self.check_guilds.start()

    @tasks.loop()
    async def check_guilds(self):
        for i in self.bot.guilds:
            if i.id not in self.data:
                self.data[i.id] = {
                    'format': '⚕️{nickname} club\'s'}

    @check_guilds.before_loop
    async def wait(self):
        return await self.bot.wait_until_ready()

    def save_json(self):
        with open('private_channels_cfg.json', 'w') as f:
            json.dump(self.data, f)

    async def cog_check(self, ctx):
        return any([x for x in ctx.author.roles if x.name == 'администратор \N{CACTUS}'])

    async def format(self, member: discord.Member):
        return prefix + self.data[member.guild.id]['format'].format(name=member.name, nickname=member.display_name, mention=member.mention, id=member.id)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if after.channel and after.channel.id == self.data[member.guild.id]['lobby']:
            overwrites = self.bot.get_channel(
                self.data[member.guild.id]['lobby']).overwrites
            new_overwrites = {
                member.guild.me: discord.PermissionOverwrite(
                    manage_channels=True
                ),
                member: discord.PermissionOverwrite(
                    manage_channels=True,
                    mute_members=True,
                    speak=True,
                    priority_speaker=True,
                    connect=True,
                    deafen_members=True,
                    use_voice_activation=True,
                    kick_members=True
                )
            }
            for i in new_overwrites:
                if i in overwrites:
                    overwrites[i].update(new_overwrites[i])
                else:
                    overwrites[i] = new_overwrites[i]
            await member.move_to(
                await member.guild.create_voice_channel(
                    name=await self.format(member),
                    category=self.bot.get_channel(
                        self.data[member.guild.id]['lobby']).category,
                    reason='Создание комнаты',
                    overwrites=overwrites
                )
            )

        if before.channel and before.channel.name.startswith(prefix) and not before.channel.members:
            await before.channel.delete(reason='Удаление комнаты')

    @commands.command(name='set-lobby', aliases=['setlobby', 'lobby'])
    async def set_channel(self, ctx: commands.Context, channel: discord.VoiceChannel):
        '''Sets lobby channel'''
        self.data[ctx.guild.id]['lobby'] = channel.id
        self.save_json()
        return await ctx.send('Done!')

    @commands.command(name='set-format', aliases=['setformat', 'format'])
    async def set_format(self, ctx: commands.Context, *, format: str):
        self.data[ctx.guild.id]['format'] = format
        self.save_json()
        await ctx.send('Preview: ' + await self.format(ctx.author))


def setup(bot):
    bot.add_cog(PrivateChannels(bot))
