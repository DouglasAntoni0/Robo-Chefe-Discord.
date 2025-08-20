# cogs/logging_system.py

import discord
from discord.ext import commands
from datetime import datetime
import asyncio

class LoggingSystemCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.log_channel_name = "📜logs"

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        log_channel = discord.utils.get(member.guild.text_channels, name=self.log_channel_name)
        if not log_channel:
            return

        # Ignora o evento se o canal não mudou (ex: apenas mutou ou desmutou o microfone)
        if before.channel == after.channel:
            return

        # --- LÓGICA DE CANAL DE VOZ CORRIGIDA ---

        # Caso 1: Membro ENTROU em uma call (estava em nenhuma antes)
        if before.channel is None and after.channel is not None:
            embed = discord.Embed(
                title="🎤 Entrada em Canal de Voz",
                description=f"{member.mention} entrou no canal de voz **{after.channel.name}**.",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            embed.set_author(name=member.name, icon_url=member.avatar.url if member.avatar else None)
            await log_channel.send(embed=embed)

        # Caso 2: Membro SAIU de uma call (não foi para nenhuma outra)
        elif before.channel is not None and after.channel is None:
            embed = discord.Embed(
                title="🔇 Saída de Canal de Voz",
                description=f"{member.mention} saiu do canal de voz **{before.channel.name}**.",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            embed.set_author(name=member.name, icon_url=member.avatar.url if member.avatar else None)
            await log_channel.send(embed=embed)

        # Caso 3: Membro se MOVEU entre calls
        elif before.channel is not None and after.channel is not None:
            embed = discord.Embed(
                title="🔄 Movido entre Canais de Voz",
                description=f"{member.mention} se moveu de **{before.channel.name}** para **{after.channel.name}**.",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            embed.set_author(name=member.name, icon_url=member.avatar.url if member.avatar else None)
            await log_channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot or message.channel.name == self.log_channel_name:
            return

        log_channel = discord.utils.get(message.guild.text_channels, name=self.log_channel_name)
        if not log_channel:
            return

        await asyncio.sleep(1)
        deleter = None
        
        try:
            async for entry in message.guild.audit_logs(limit=5, action=discord.AuditLogAction.message_delete):
                if entry.target.id == message.author.id and entry.extra.channel.id == message.channel.id:
                    deleter = entry.user
                    break
        except discord.Forbidden:
            deleter = None # Não temos permissão para ver o log de auditoria

        embed_delete = discord.Embed(
            title="🗑️ Mensagem Apagada",
            description=f"Uma mensagem de {message.author.mention} foi apagada no canal {message.channel.mention}.",
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )

        if message.content:
            embed_delete.add_field(name="Conteúdo da Mensagem", value=f"```{message.content}```", inline=False)
        
        if deleter:
            embed_delete.set_footer(text=f"Apagada por: {deleter.name}")
        else:
            embed_delete.set_footer(text="Não foi possível identificar quem apagou (provavelmente o próprio autor).")
            
        await log_channel.send(embed=embed_delete)

async def setup(bot):
    await bot.add_cog(LoggingSystemCog(bot))