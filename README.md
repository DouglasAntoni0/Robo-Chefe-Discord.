# 🤖 ROBÔ CHEFE - O Gerente do Discord

Bem-vindo ao repositório oficial do **Robô Chefe**. Este é um bot de administração, atendimento e utilidades focado em manter a ordem na casa (e garantir que ninguém faça bagunça).

Atualmente hospedado e rodando liso na **Koyeb**. 🚀

---

## 🛠️ O que esse robô faz?

Ele não tira café, mas faz quase todo o resto:

* **📩 Sistema de Tickets Avançado:**
    * Cria canais privados para atendimento.
    * Salva o ID do usuário para garantir contato.
    * **Pesquisa de Satisfação:** Ao fechar o ticket, o bot vai no PV do usuário perguntar a nota (1-5), opinião e sugestões, e manda o relatório para os Adms.
* **🛡️ Moderação:** Ban, Kick, Mute (o kit completo para lidar com engraçadinhos).
* **📊 Logs:** Monitora mensagens apagadas, editadas e entra/sai de membros.
* **🎭 Reaction Roles:** Dá cargos automaticamente quando alguém reage a uma mensagem.
* **🎨 Embed Builder:** Cria mensagens bonitonas e organizadas.

---

## ⚠️ AVISO DE PROPRIEDADE E DIREITOS (LEIA!)

Este código está público no GitHub para **fins de estudo e portfólio**.

**📜 A Licença "DOUGLAS-V1" (Lei do Chefe):**

1.  **Pode olhar?** 👀 Pode. Fique à vontade para aprender como funciona.
2.  **Pode usar de base?** 📚 Pode, desde que você não faça um "Ctrl+C / Ctrl+V" safado e diga que foi você que criou.
3.  **Pode vender?** 🚫 **NEM PENSAR.** Se eu ver alguém vendendo esse código, o processo vem a galope (ou eu mando o bot travar seu Discord, brincadeira... ou não).
4.  **Autoria:** Se usar partes deste código, tenha a decência de manter os créditos ou pagar um salgado pro desenvolvedor.

**Resumo:** Não seja um "kibeiro". O código é aberto, mas a autoria é do **Douglas Antonio**. Respeite para ser respeitado. 🤝

---

## 🚀 Tecnologias

* **Linguagem:** Python 3.12+
* **Biblioteca:** Discord.py
* **Hospedagem:** Koyeb (Worker)

---

## 🔧 Como rodar (para devs)

Se você for rodar isso localmente (no seu PC):

1.  Clone o repositório.
2.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
3.  Crie um arquivo `.env` ou configure as variáveis de ambiente com seu `DISCORD_TOKEN`.
4.  Rode o bot:
    ```bash
    python main.py
    ```

---

*Desenvolvido com ☕ e ódio a bugs por Douglas Antonio.*
