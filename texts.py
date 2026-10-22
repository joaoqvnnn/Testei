TEXTS = {
"block_channel": "❗️ <b>Para utilizar nosso serviço é obrigatório que você entre no nosso grupo.</b>",

"welcome": (
"🎬 <b>Bem-vindo à Larizinha Store!</b> ✨\n"
"A sua central de streamings com entrega 100% automática.\n\n"
"Pagou, recebeu. Sem filas, sem precisar falar com atendente, 24 horas por dia! ⚡️\n\n"
"🛡 <b>Segurança e Suporte:</b>\n"
"Mais de 12.000 clientes já passaram por aqui.\n"
"Participe da nossa comunidade e veja as referências\n\n"
"💠 <b>Seus Dados:</b>\n"
"├👤 ID: {id}\n"
"└💰 Saldo Atual: R$ {saldo}\n\n"
"👇 <b>COMO COMEÇAR:</b>\n"
"Clique no botão \"🛍 Comprar Produtos\" abaixo para ver nosso catálogo e escolher sua tela!"
),

"catalog": (
"📱 <b>Lari Contas | Catálogo de Serviços</b>\n"
"🔗🔗🔗🔗🔗🔗🔗🔗🔗🔗🔗\n\n"
"💰| <b>Saldo da Carteira:</b> R$ {saldo}\n\n"
"⬇️ Selecione uma categoria abaixo para ver nossos planos:"
),

"product": (
"🔥 <b>OPORTUNIDADE EXCLUSIVA</b> 🔥\n"
"🚀 <b>{produto}</b>\n\n"
"🟢 <b>DISPONÍVEL AGORA</b>\n"
"├ 💵 Preço: R$ {preco}\n"
"├ 💰 Seu Saldo: R$ {saldo}\n"
"└ 📦 Estoque: {estoque}\n\n\n"
"📝 <b>Descrição:</b>\n{descricao}\n\n\n"
"📊 <b>Estatísticas em tempo real:</b>\n"
"⚡️ Já foram vendidas {vendidos} unidades!\n"
"👀 {views} pessoas estão vendo isso agora.\n\n"
"🛡 <b>Garantia:</b> 30 dias\n"
"✅ Compra segura. Ao adquirir, concorda com /termos"
),

"delivery_ok": (
"🎉 <b>VENDA APROVADA COM SUCESSO!</b> 🎉\n\n"
"💰 Produto: {produto}\n"
"👤 Cliente: {nome}\n"
"🆔 ID: {id}\n"
"💵 Valor: R$ {valor}\n"
"📧 Email: ||{email}||\n"
"🔒 Senha: ||{senha}||\n"
"✅ Obrigado pela compra! Seu acesso já foi liberado.\n"
"🔗 {link_acesso}"
),

"insufficient": (
"❌ <b>Saldo insuficiente!</b>\n\n"
"💰 Seu saldo: R$ {saldo}\n"
"💵 Valor do produto: R$ {preco}\n"
"📉 Faltam: R$ {faltam}\n\n"
"💡 Deseja gerar um PIX no valor de R$ {faltam} para completar a compra?"
),

"insufficient_multi": (
"❌ <b>Saldo insuficiente!</b>\n\n"
"💰 Seu saldo: R$ {saldo}\n"
"💵 Valor total: R$ {valor_total}\n"
"📉 Faltam: R$ {faltam}\n\n"
"💡 Deseja gerar um PIX para completar a compra?"
),

"qty_prompt": (
"Quantos logins deseja comprar?\n\n"
"📦 Estoque disponível: {estoque}\n\n"
"💡 Digite /cancelar a qualquer momento para sair."
),

"pix_generating": "⏳ Gerando pagamento...",

"pix_qr": (
"💰 <b>Comprar Saldo com Pix Automático (PurinCash):</b>\n\n"
"⏱️ Expira em: 10 minutos\n"
"💵 Valor: R$ {valor}\n"
"✨ ID da Recarga: {id_recarga}\n\n"
"📃 Atenção: Este código é válido para apenas um único pagamento.\n"
"Se você utilizá-lo mais de uma vez, o saldo adicional será perdido sem direito a reembolso.\n\n"
"💎 Pix Copia e Cola:\n<code>{codigo_pix}</code>\n\n"
"💡 Dica: Clique no código acima para copiar.\n\n"
"🇧🇷 Após o pagamento, seu saldo será liberado instantaneamente."
),

"pix_pending": (
"⏳ <b>Ainda não identificamos seu pagamento.</b>\n\n"
"💵 Valor: R$ {valor}\n"
"✨ ID da Recarga: {id_recarga}\n"
"⏱️ Expira em: {minutos} minutos\n\n"
"Caso já tenha pago, aguarde alguns instantes."
),

"pix_expired": (
"⌛️ <b>PAGAMENTO PIX EXPIRADO</b>\n\n"
"⚠️ O tempo limite para realizar este pagamento foi excedido.\n\n"
"🆔 Referência do Pagamento: {referencia}\n"
"💸 Valor Solicitado: R$ {valor}"
),

"profile": (
"👤 <b>Meu perfil</b>\n\n"
"🔍 Veja aqui os detalhes da sua conta:\n\n"
"- 👤 <b>Informações:</b>\n"
"🆔 ID da Carteira: {id}\n"
"💰 Saldo Atual: R$ {saldo}\n"
"📲 Seu Whatsapp: <b><a href=\"wa.me/55{whatsapp}\">{whatsapp}</a></b>\n\n"
"─── 📊 <b>Suas Movimentações:</b>\n"
"ー 🛒 Compras Realizadas: {compras}\n"
"ー 💰 Total Gasto Em Compras: R$ {total_gasto}\n"
"ー 💠 Pix Inseridos: R$ {pix_inseridos}\n"
"ー 🎁 Gifts Resgatados: R$ {gifts}"
),

"history_empty_active": (
"Você não tem compras ativas (não vencidas) no bot.\n\n"
"Use o botão abaixo para ver todas as compras."
),
"history_empty_all": (
"Você não tem compras no bot. Quando comprar alguma conta, as informações dela ficarão exibidas aqui."
),
"history_item": (
"🛍 <b>Compras:</b> {n}\n\n"
"⏰ Data da compra: {data}\n"
"📆 Vencimento: {vencimento}\n"
"💰 Valor: R$ {valor}\n"
"🎫 ID da compra: {id_compra}\n"
"⚜️ Serviço: {servico}\n"
"📧 Email: {email}\n"
"🔐 Senha: {senha}\n"
"📃 Nota: Use o link abaixo para ativar:\n\n"
"<a href=\"{link}\">CLIQUE AQUI PARA ATIVAR</a>\n\n"
"Ref: {ref}"
),

"gift_prompt": (
"🎁 <b>RESGATAR GIFT CARD</b>\n\n"
"Digite o código do seu gift card abaixo:\n\n"
"Exemplo: ABC123XYZ456"
),
"gift_not_found": "Gift não encontrado.",
"gift_success": (
"🎉 <b>GIFT CARD RESGATADO COM SUCESSO!</b> 🎁\n\n"
"💳 <b>Código:</b> <code>||{codigo}||</code>\n"
"👤 <b>Cliente:</b> {nome}\n"
"🆔 <b>ID:</b> <code>{id}</code>\n"
"💰 <b>Valor:</b> R$ {valor}\n"
"📦 <b>Produto:</b> {produto}\n\n"
"✅ Seu acesso foi liberado!\n"
"🔗 <b>Link:</b>\n\n"
"💚 Obrigado pela preferência!"
),

"edit_data": (
"✏️ <b>Alterar Dados</b>\n\n"
"Selecione o dado que deseja alterar:\n\n"
"📱 WhatsApp: {whatsapp}"
),
"edit_whatsapp_prompt": (
"📱 Envie seu número de WhatsApp\n\n"
"Formato: DDD + Número (apenas números)\n"
"Exemplo: 11999998888\n\n"
"⚠️ Envie <b>remover</b> para remover o número cadastrado."
),
"edit_whatsapp_invalid": "❌ Número inválido! Envie DDD + Número (10 a 13 dígitos).",
"edit_whatsapp_ok": "✅ WhatsApp atualizado com sucesso!",
"edit_whatsapp_removed": "✅ WhatsApp removido com sucesso!",

"recharge": (
"🆔| <b>ID da Carteira:</b> {id}\n"
"💰| <b>Saldo Disponível:</b> R$ {saldo}\n\n"
"📍 Opte por 💠 <b>Pix Rápido</b> para que seu saldo seja creditado imediatamente.\n\n"
"💡 Selecione uma opção para recarregar:"
),
"recharge_value_prompt": (
"ℹ️ Informe o valor que deseja recarregar:\n\n"
"🔻 Recarga mínima: R$ 4,00\n\n"
"⚠️ Por favor, envie o valor que deseja recarregar agora.\n"
"Ao realizar um depósito você declara ter lido e estar de acordo com nossos /termos\n\n"
"🎁 <b>Bônus de recarga:</b> 10%\n"
"❗️ Recarga mínima para ganhar o bônus: R$15,00"
),
"recharge_success": (
"✅ <b>Crédito adicionado com sucesso!</b>\n\n"
"💰 Valor: R$ {valor}\n"
"🕒 Data: {data}\n"
"🕒 Hora: {hora}"
),

"affiliates": (
"💰 <b>PROGRAMA DE AFILIADOS</b>\n\n"
"⚙️ Status: {status}\n"
"🧲 Sua comissão: {comissao}% (de todas recargas do indicado)\n\n"
"👥 Indicações: {indicacoes}\n"
"🪙 Total ganho: R$ {total_ganho}\n"
"📊 Média: R$ {media}\n"
"💰 Saque mínimo: R$ {saque_minimo}\n\n\n"
"🌱| Nível: {nivel}\n"
"🎯 Próxima meta: {meta} ({restantes} restantes)\n\n"
"ℹ️ <b>INFO:</b> Seus indicados continuarão gerando comissão para sempre.\n"
"A comissão pode ser alterada a qualquer momento, fique atento aos avisos.\n"
"🔗 Seu link:\n"
"<a href=\"https://t.me/{bot}?start={id}\">https://t.me/{bot}?start={id}</a>"
),

"top_ranking": (
"🏆 <b>TOP {titulo}</b>\n\n{lista}"
),

"channel_sale": (
"💰 <b>VENDA APROVADA!</b>\n\n"
"👤 Cliente: {nome}***\n"
"📦 {produto}\n"
"💵 R$ {valor}\n\n"
"✅ Entrega automática e instantânea!\n\n"
"📲 Compre aqui: @{bot}"
),

"abandoned_cart": (
"👋 Ei, você esqueceu algo!\n\n"
"Notamos que você estava olhando o produto <b>{produto}</b> mas não finalizou a compra.\n\n"
"💰 Valor: R$ {preco}\n\n"
"🔥 <b>ATENÇÃO:</b> Restam apenas {estoque} unidades! Garanta o seu!\n\n"
"🎁 Que tal finalizar agora?\n"
"Seu produto está esperando por você!\n\n"
"Se tiver alguma dúvida, estamos aqui para ajudar!"
),
"abandoned_recharge": (
"👋 Ei, você começou uma recarga e não finalizou!\n\n"
"💵 Valor: R$ {valor}\n\n"
"🎁 Recarregue agora e ganhe 10% de bônus!\n"
"Seu saldo está esperando por você."
),

"access_denied": (
"🚫 <b>Acesso negado!</b>\n\n"
"Você não comprou este produto no bot.\n\n"
"Para acessar, efetue a compra normalmente."
),
}

DEFAULT_BUTTONS = {
    "welcome_buy": "🛍 Comprar Produtos",
    "welcome_store": "🛒 Abrir loja",
    "welcome_recharge": "💳 Recarregar saldo",
    "welcome_profile": "👤 Meu perfil",
    "welcome_affiliates": "🤝 Afiliados",
    "welcome_support": "💬 Atendimento",
    "welcome_search": "🔎 Pesquisar serviço",
    "welcome_top": "🏆 Top compradores",

    "back": "⬅️ Voltar",
    "prev_page": "⬅️ Página anterior",
    "next_page": "Próxima página ➡️",

    "buy": "💳 Comprar",
    "buy_multi": "🛒 Comprar mais de um",
    "delivery_link": "🔗 Link de acesso",
    "activate_on": "🔴 Ativar",
    "activate_off": "🟢 Ativar",
    "advance": "Avançar >>",
    "prev": "<< Voltar",

    "profile_history": "📜 Histórico de compras",
    "profile_gift": "🎁 Resgatar gift card",
    "profile_edit": "✏️ Alterar dados",

    "history_all": "Ver todas",
    "history_active": "🟢 Apenas Ativas",

    "gift_cancel": "Cancelar",

    "edit_cancel": "⬅️ Voltar",

    "recharge_pix": "💠 Pix instantâneo",
    "recharge_cancel": "Cancelar",

    "pix_copy": "📋 Copiar Pix copia e cola",
    "pix_wait": "⏳ Aguardando o pagamento",
    "pix_paid": "✅ Já paguei",
    "pix_new": "🔄 Gerar novo Pix",
    "pix_cancel": "❌ Cancelar",

    "aff_activate": "✅ Ativar",
    "aff_points": "🪙 Trocar pontos por saldo",
    "aff_pdf": "📄 Exportar PDF",

    "top_servicos": "Serviços",
    "top_recargas": "Recargas",
    "top_saldo": "Saldo",
    "top_gift": "Gift card",
    "top_comprar": "Comprar",

    "channel_ver_compras": "🔗 Ver Compras",
    "channel_comprar": "🛒 Comprar também",
    "abandon_buy": "🛒 Comprar Agora",
    "abandon_view": "👀 Ver Detalhes",
}
