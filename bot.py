import logging, asyncio, uuid, io, aiosqlite
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply,
    InlineQueryResultArticle, InputTextMessageContent,
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ChatMemberHandler, InlineQueryHandler, filters, ContextTypes,
)
from telegram.constants import ChatMemberStatus, ParseMode

# Imports para o PDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch

from config import *
from database import *
from texts import TEXTS
import payments

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ---------- helpers ----------
async def txt(key, **kw):
    t = await get_text(key)
    try:
        return t.format(**kw)
    except (KeyError, IndexError):
        return t

async def btn(key, cb=None, url=None, sw=None, copy_text=None):
    label = await get_btn(key)
    if url:
        return InlineKeyboardButton(label, url=url)
    if sw:
        return InlineKeyboardButton(label, switch_inline_query_current_chat=sw)
    if copy_text:
        return InlineKeyboardButton(label, copy_text=copy_text)
    return InlineKeyboardButton(label, callback_data=cb or "noop")

async def is_member(bot, uid):
    if not GROUP_ID:
        return True
    try:
        m = await bot.get_chat_member(GROUP_ID, uid)
        return m.status in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except Exception:
        return False

async def fmt_brl(v):
    return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

async def get_ctx_user(update):
    tg = update.effective_user
    row = await get_or_create_user(tg)
    return tg, row

# ---------- GERAR PDF ----------
def generate_pdf(user_id, username, nome, total_ganho, indicacoes):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    p.setFont("Helvetica-Bold", 24)
    p.drawString(1 * inch, 10 * inch, "Bellamy Store")
    p.setFont("Helvetica", 12)
    p.drawString(1 * inch, 9.6 * inch, "Relatório de Afiliados")
    
    p.setFont("Helvetica-Bold", 14)
    p.drawString(1 * inch, 8.8 * inch, "Dados do Afiliado:")
    p.setFont("Helvetica", 12)
    p.drawString(1 * inch, 8.4 * inch, f"ID: {user_id}")
    p.drawString(1 * inch, 8.1 * inch, f"Username: @{username if username else 'N/A'}")
    p.drawString(1 * inch, 7.8 * inch, f"Nome: {nome}")
    
    dt_br = datetime.now(ZoneInfo("America/Sao_Paulo"))
    p.drawString(1 * inch, 7.2 * inch, f"Data do Relatório: {dt_br.strftime('%d/%m/%Y às %H:%M')} (Brasília)")
    
    p.setFont("Helvetica-Bold", 14)
    p.drawString(1 * inch, 6.4 * inch, "Resumo Financeiro:")
    p.setFont("Helvetica", 12)
    p.drawString(1 * inch, 6.0 * inch, f"Total de Indicações: {indicacoes}")
    p.drawString(1 * inch, 5.7 * inch, f"Total Ganho Acumulado: R$ {fmt_brl(total_ganho)}")
    
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(1 * inch, 1 * inch, "Este documento é gerado automaticamente pelo sistema Bellamy Store.")
    
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

# ---------- START / BLOQUEIO / BOAS-VINDAS ----------
async def send_block(update, context):
    row = [InlineKeyboardButton("📢 Entrar no grupo", url=GROUP_URL)]
    await update.effective_message.reply_text(
        await get_text("block_channel"),
        reply_markup=InlineKeyboardMarkup([row]),
        parse_mode=ParseMode.HTML,
    )

async def send_welcome(update, context, edit=False):
    tg, u = await get_ctx_user(update)
    uid, saldo = u[0], u[3] or 0
    text = await txt("welcome", id=uid, saldo=await fmt_brl(saldo))
    row1 = [await btn("welcome_buy", cb="nav:catlist:0")]
    row2 = [await btn("welcome_store", url=STORE_URL),
            await btn("welcome_recharge", cb="nav:recharge")]
    row3 = [await btn("welcome_profile", cb="nav:profile"),
            await btn("welcome_affiliates", cb="nav:affiliates")]
    row4 = [await btn("welcome_support", url=SUPPORT_URL),
            await btn("welcome_search", sw="procurar ")]
    row5 = [await btn("welcome_top", cb="nav:top:servicos")]
    markup = InlineKeyboardMarkup([row1, row2, row3, row4, row5])
    if edit and update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    else:
        await update.effective_message.reply_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)

async def cmd_start(update, context):
    tg = update.effective_user
    arg = context.args[0] if context.args else ""

    if not await is_member(context.bot, tg.id):
        context.user_data["pending_arg"] = arg
        return await send_block(update, context)

    ref = None
    if arg.isdigit():
        ref = int(arg)
    await get_or_create_user(tg, referred_by=ref)

    if arg.startswith("ver_compra_"):
        pid = int(arg.split("_")[-1])
        return await deep_ver_compra(update, context, pid)
    if arg.startswith("category=="):
        cid = int(arg.split("==")[1])
        return await show_catalog(update, context, cid, 0, send_new=True)
    if arg.startswith("buy=="):
        pid = int(arg.split("==")[1])
        return await show_product(update, context, pid, send_new=True)

    await send_welcome(update, context)

async def cmd_debug(update, context):
    tg = update.effective_user
    lines = [f"👤 Seu ID: <code>{tg.id}</code>"]
    lines.append(f"GROUP_ID: <code>{repr(GROUP_ID)}</code>")
    lines.append(f"GROUP_URL: <code>{repr(GROUP_URL)}</code>")
    lines.append(f"SUPPORT_URL: <code>{repr(SUPPORT_URL)}</code>")
    lines.append(f"BOT_USERNAME: <code>{repr(BOT_USERNAME)}</code>")
    lines.append(f"STORE_URL: <code>{repr(STORE_URL)}</code>")
    lines.append(f"WEBHOOK_URL: <code>{repr(WEBHOOK_URL)}</code>")
    try:
        me = await context.bot.get_me()
        lines.append(f"Bot: @{me.username} (id {me.id})")
    except Exception as e:
        lines.append(f"getMe erro: {e}")
    if GROUP_ID:
        try:
            m = await context.bot.get_chat_member(GROUP_ID, tg.id)
            lines.append(f"✅ Você no grupo: <b>{m.status}</b>")
        except Exception as e:
            lines.append(f"❌ Você no grupo: <code>{e}</code>")
        try:
            me = await context.bot.get_me()
            m2 = await context.bot.get_chat_member(GROUP_ID, me.id)
            lines.append(f"✅ Bot no grupo: <b>{m2.status}</b>")
        except Exception as e:
            lines.append(f"❌ Bot no grupo: <code>{e}</code>")
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)

async def on_chat_member(update, context):
    cm = update.chat_member
    if not cm:
        return
    if str(cm.chat.id) != str(GROUP_ID):
        return
    old, new = cm.old_chat_member.status, cm.new_chat_member.status
    entrou = new in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER) \
             and old not in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    if not entrou:
        return
    user = cm.new_chat_member.user
    await get_or_create_user(user)
    try:
        u = await get_user(user.id)
        text = await txt("welcome", id=u[0], saldo=await fmt_brl(u[3] or 0))
        row1 = [await btn("welcome_buy", cb="nav:catlist:0")]
        row2 = [await btn("welcome_store", url=STORE_URL), await btn("welcome_recharge", cb="nav:recharge")]
        row3 = [await btn("welcome_profile", cb="nav:profile"), await btn("welcome_affiliates", cb="nav:affiliates")]
        row4 = [await btn("welcome_support", url=SUPPORT_URL), await btn("welcome_search", sw="procurar ")]
        row5 = [await btn("welcome_top", cb="nav:top:servicos")]
        await context.bot.send_message(
            user.id, text,
            reply_markup=InlineKeyboardMarkup([row1,row2,row3,row4,row5]),
            parse_mode=ParseMode.HTML)
    except Exception as e:
        log.warning(f"welcome dm failed: {e}")

# ---------- CATÁLOGO ----------
async def show_catalog(update, context, cid, page=0, send_new=False):
    _, u = await get_ctx_user(update)
    saldo = u[3] or 0
    cats = await get_categories()
    text = await txt("catalog", saldo=await fmt_brl(saldo))
    rows = []
    for c in cats:
        rows.append([InlineKeyboardButton(f"{c[2]} {c[1]}", callback_data=f"nav:cat:{c[0]}:0")])
    rows.append([await btn("back", cb="nav:welcome")])
    markup = InlineKeyboardMarkup(rows)
    if send_new:
        await update.effective_message.reply_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    else:
        await update.callback_query.edit_message_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)

async def show_category_products(update, context, cid, page=0):
    _, u = await get_ctx_user(update)
    saldo = u[3] or 0
    prods = await get_products_by_cat(cid, page)
    total = await count_products_by_cat(cid)
    text = await txt("catalog", saldo=await fmt_brl(saldo))
    rows = []
    for p in prods:
        rows.append([InlineKeyboardButton(
            f"{p[2]} - R$ {await fmt_brl(p[3])}", callback_data=f"prod:{p[0]}")])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️", callback_data=f"nav:cat:{cid}:{page-1}"))
    if (page+1)*6 < total:
        nav.append(InlineKeyboardButton("➡️", callback_data=f"nav:cat:{cid}:{page+1}"))
    if nav:
        rows.append(nav)
    rows.append([await btn("back", cb="nav:catlist:0")])
    await update.callback_query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(rows), parse_mode=ParseMode.HTML)

async def show_product(update, context, pid, send_new=False):
    _, u = await get_ctx_user(update)
    p = await get_product(pid)
    if not p:
        return
    await inc_views(pid)
    text = await txt("product",
        produto=p[2], preco=await fmt_brl(p[3]), saldo=await fmt_brl(u[3] or 0),
        estoque=p[5], descricao=p[4] or "—", vendidos=p[6], views=p[7]+1)
    rows = [
        [await btn("buy", cb=f"buy:{pid}")],
        [await btn("buy_multi", cb=f"buyq:{pid}")],
        [await btn("back", cb=f"nav:cat:{p[1]}:0")],
    ]
    await track_abandoned(u[0], pid, "cart", p[3])
    markup = InlineKeyboardMarkup(rows)
    if send_new:
        await update.effective_message.reply_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    else:
        await update.callback_query.edit_message_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)

# ---------- COMPRA SIMPLES ----------
async def do_buy(update, context, pid):
    tg, u = await get_ctx_user(update)
    p = await get_product(pid)
    if not p:
        return
    price = p[3]
    saldo = u[3] or 0
    if saldo >= price:
        email = f"user{tg.id}@lari.com"
        senha = uuid.uuid4().hex[:10]
        link = f"https://ativar.lari/{uuid.uuid4().hex[:8]}"
        purchase_id = await add_purchase(u[0], pid, price, email, senha, link)
        await add_saldo(u[0], -price)
        await decrement_stock(pid, 1)
        await clear_abandoned(u[0], pid)
        text = await txt("delivery_ok",
            produto=p[2], nome=tg.full_name, id=u[0],
            valor=await fmt_brl(price), email=email, senha=senha, link_acesso=link)
        rows = [
            [InlineKeyboardButton(await get_btn("delivery_link"), url=link)],
            [InlineKeyboardButton(await get_btn("activate_on"), callback_data=f"dlv:on:{purchase_id}")],
        ]
        await context.bot.send_message(tg.id, text, reply_markup=InlineKeyboardMarkup(rows), parse_mode=ParseMode.HTML)
        await post_group_sale(context.bot, tg, p, price)
        await update.callback_query.answer("Compra aprovada!")
    else:
        faltam = round(price - saldo, 2)
        text = await txt("insufficient",
            saldo=await fmt_brl(saldo), preco=await fmt_brl(price), faltam=await fmt_brl(faltam))
        rows = [
            [InlineKeyboardButton(f"💠 Gerar Pix R$ {await fmt_brl(faltam)}", callback_data=f"pix:buy:{pid}:{faltam}:1")],
            [await btn("pix_cancel", cb="nav:welcome")],
        ]
        await context.bot.send_message(tg.id, text, reply_markup=InlineKeyboardMarkup(rows), parse_mode=ParseMode.HTML)
        await update.callback_query.answer()

async def post_group_sale(bot, tg, p, price):
    if not GROUP_ID:
        return
    text = await txt("group_sale",
        nome=tg.full_name[:8], produto=p[2], valor=await fmt_brl(price), bot=BOT_USERNAME)
    rows = [
        [InlineKeyboardButton(await get_btn("group_ver_compras"),
            url=f"https://t.me/{BOT_USERNAME}?start=ver_compra_{p[0]}")],
        [InlineKeyboardButton(await get_btn("group_comprar"),
            url=f"https://t.me/{BOT_USERNAME}?start=category=={p[1]}")],
    ]
    try:
        await bot.send_message(GROUP_ID, text, reply_markup=InlineKeyboardMarkup(rows), parse_mode=ParseMode.HTML)
    except Exception as e:
        log.warning(f"grupo post: {e}")

# ---------- COMPRA MÚLTIPLA ----------
async def ask_qty(update, context, pid):
    p = await get_product(pid)
    text = await txt("qty_prompt", estoque=p[5])
    msg = await context.bot.send_message(
        update.effective_chat.id, text,
        reply_markup=ForceReply(selective=True), parse_mode=ParseMode.HTML)
    context.user_data["qty_pid"] = pid
    context.user_data["qty_msg_id"] = msg.message_id

async def handle_qty_text(update, context):
    if "qty_pid" not in context.user_data:
        return
    try:
        qty = int(update.message.text.strip())
    except Exception:
        return await update.message.reply_text("❌ Envie um número válido.", reply_to_message_id=update.message.message_id)
    pid = context.user_data.pop("qty_pid")
    await do_buy_multi(update, context, pid, qty, reply_to=update.message)

async def do_buy_multi(update, context, pid, qty, reply_to=None):
    tg, u = await get_ctx_user(update)
    p = await get_product(pid)
    price = p[3] * qty
    saldo = u[3] or 0
    if saldo >= price:
        purchases = []
        for _ in range(qty):
            email = f"u{tg.id}_{uuid.uuid4().hex[:4]}@lari.com"
            senha = uuid.uuid4().hex[:10]
            link = f"https://ativar.lari/{uuid.uuid4().hex[:8]}"
            i = await add_purchase(u[0], pid, p[3], email, senha, link)
            purchases.append({"id": i, "email": email, "senha": senha, "link": link})
        await add_saldo(u[0], -price)
        await decrement_stock(pid, qty)
        await clear_abandoned(u[0], pid)
        context.user_data["multi"] = {
            "pid": pid, "qty": qty, "idx": 0,
            "items": purchases, "produto": p[2], "valor_unit": p[3]}
        await render_multi(update, context, new=True)
    else:
        faltam = round(price - saldo, 2)
        text = await txt("insufficient_multi",
            saldo=await fmt_brl(saldo), valor_total=await fmt_brl(price), faltam=await fmt_brl(faltam))
        rows = [
            [InlineKeyboardButton(f"💠 Gerar Pix R$ {await fmt_brl(faltam)}",
                callback_data=f"pix:buymulti:{pid}:{qty}:{faltam}")],
            [await btn("pix_cancel", cb="nav:welcome")],
        ]
        await context.bot.send_message(
            update.effective_chat.id, text,
            reply_markup=InlineKeyboardMarkup(rows), parse_mode=ParseMode.HTML)

async def render_multi(update, context, new=False, edit_query=None):
    d = context.user_data["multi"]
    i = d["idx"]
    item = d["items"][i]
    total = d["qty"]
    tg = update.effective_user
    text = await txt("delivery_ok",
        produto=d["produto"], nome=tg.full_name, id=tg.id,
        valor=await fmt_brl(d["valor_unit"]*total),
        email=item["email"], senha=item["senha"], link_acesso=item["link"])
    rows = [
        [InlineKeyboardButton(await get_btn("delivery_link"), url=item["link"])],
        [InlineKeyboardButton(await get_btn("activate_on"), callback_data=f"dlv:on:{item['id']}")],
    ]
    nav = []
    if i > 0:
        nav.append(InlineKeyboardButton(await get_btn("prev"), callback_data="multi:prev"))
    nav.append(InlineKeyboardButton(f"{i+1}/{total}", callback_data="noop"))
    if i+1 < total:
        nav.append(InlineKeyboardButton(await get_btn("advance"), callback_data="multi:next"))
    rows.append(nav)
    if edit_query:
        await edit_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(rows), parse_mode=ParseMode.HTML)
    else:
        await context.bot.send_message(update.effective_chat.id, text,
            reply_markup=InlineKeyboardMarkup(rows), parse_mode=ParseMode.HTML)

# ---------- PROFILE / HISTORY / GIFT / EDIT ----------
async def show_profile(update, context):
    _, u = await get_ctx_user(update)
    st = await user_stats(u[0])
    wa = u[4] or "—"
    text = await txt("profile",
        id=u[0], saldo=await fmt_brl(u[3] or 0), whatsapp=wa,
        compras=st["compras"], total_gasto=await fmt_brl(st["total_gasto"]),
        pix_inseridos=await fmt_brl(st["pix"]), gifts=await fmt_brl(st["gifts"]))
    rows = [
        [await btn("profile_history", cb="prof:history")],
        [await btn("profile_gift", cb="prof:gift")],
        [await btn("profile_edit", cb="prof:edit")],
        [await btn("back", cb="nav:welcome")],
    ]
    await update.callback_query.edit_message_text(
        text, 
        reply_markup=InlineKeyboardMarkup(rows), 
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

async def show_history(update, context, page=0, active_only=True):
    _, u = await get_ctx_user(update)
    total = await count_user_purchases(u[0], active_only=active_only)
    
    if total == 0:
        if active_only:
            all_count = await count_user_purchases(u[0], active_only=False)
            if all_count > 0:
                text = await get_text("history_empty_active")
                rows = [
                    [await btn("history_all", cb="prof:history:all:0")],
                    [await btn("back", cb="nav:profile")]
                ]
            else:
                text = await get_text("history_empty_all")
                rows = [[await btn("back", cb="nav:profile")]]
        else:
            text = await get_text("history_empty_all")
            rows = [[await btn("history_active", cb="prof:history:active:0")],
                    [await btn("back", cb="nav:profile")]]
            
        return await update.callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(rows), parse_mode=ParseMode.HTML, disable_web_page_preview=True)

    items = await user_purchases(u[0], active_only=active_only, page=page, per_page=1)
    item = items[0]
    p = await get_product(item[2])
    data = item[7][:10] if item[7] else "—"
    venc = item[8][:10] if item[8] else "—"
    text = await txt("history_item",
        n=f"{page+1}/{total}",
        data=data, vencimento=venc, valor=await fmt_brl(item[3]),
        id_compra=item[0], servico=p[2] if p else "—",
        email=item[4], senha=item[5], link=item[6], ref=f"REF{item[0]:06d}")
    rows = []
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️", callback_data=f"prof:history:prev:{page-1}:{int(active_only)}"))
    nav.append(InlineKeyboardButton(f"{page+1}/{total}", callback_data="noop"))
    if (page+1) < total:
        nav.append(InlineKeyboardButton("➡️", callback_data=f"prof:history:next:{page+1}:{int(active_only)}"))
    if nav:
        rows.append(nav)
        
    if active_only:
        rows.append([await btn("history_all", cb="prof:history:all:0")])
    else:
        rows.append([await btn("history_active", cb="prof:history:active:0")])
        
    rows.append([await btn("back", cb="nav:profile")])
    await update.callback_query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(rows), parse_mode=ParseMode.HTML, disable_web_page_preview=True)

async def show_gift(update, context):
    text = await get_text("gift_prompt")
    rows = [[await btn("gift_cancel", cb="nav:profile")]]
    await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(rows), parse_mode=ParseMode.HTML)
    context.user_data["await_gift"] = True

async def handle_gift_code(update, context):
    if not context.user_data.get("await_gift"):
        return
    code = update.message.text.strip().upper()
    g = await get_gift(code)
    if not g:
        return await update.message.reply_text(await get_text("gift_not_found"), reply_to_message_id=update.message.message_id)
    context.user_data.pop("await_gift")
    tg, u = await get_ctx_user(update)
    await use_gift(code, u[0])
    p = await get_product(g[3])
    text = await txt("gift_success",
        codigo=code, nome=tg.full_name, id=u[0],
        valor=await fmt_brl(g[2]), produto=p[2] if p else "—")
    rows = [
        [InlineKeyboardButton(await get_btn("delivery_link"),
            url=f"https://t.me/{BOT_USERNAME}?start=category=={p[1] if p else 0}")],
        [InlineKeyboardButton(await get_btn("activate_on"), callback_data=f"gift:on:{g[0]}")],
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(rows), parse_mode=ParseMode.HTML, disable_web_page_preview=True)

async def show_edit_data(update, context):
    _, u = await get_ctx_user(update)
    wa = u[4] or "—"
    text = await txt("edit_data", whatsapp=wa)
    rows = [
        [InlineKeyboardButton(
            f"📱 WhatsApp: {wa}" if wa != "—" else "📱 WhatsApp",
            callback_data="prof:edit:wa")],
        [await btn("back", cb="nav:profile")],
    ]
    await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(rows), parse_mode=ParseMode.HTML)

async def ask_whatsapp(update, context):
    text = await get_text("edit_whatsapp_prompt")
    await context.bot.send_message(update.effective_chat.id, text,
        reply_markup=ForceReply(selective=True), parse_mode=ParseMode.HTML)
    context.user_data["await_wa"] = True

async def handle_whatsapp(update, context):
    if not context.user_data.get("await_wa"):
        return
    tg, u = await get_ctx_user(update)
    v = update.message.text.strip().lower()
    
    if v == "remover":
        await set_whatsapp(u[0], None)
        context.user_data.pop("await_wa")
        return await update.message.reply_text(await get_text("edit_whatsapp_removed"), reply_to_message_id=update.message.message_id)
    
    digits = "".join(ch for ch in v if ch.isdigit())
    if len(digits) < 10 or len(digits) > 13:
        return await update.message.reply_text(await get_text("edit_whatsapp_invalid"), reply_to_message_id=update.message.message_id)
    
    await set_whatsapp(u[0], digits)
    context.user_data.pop("await_wa")
    await update.message.reply_text(await get_text("edit_whatsapp_ok"), reply_to_message_id=update.message.message_id)

# ---------- RECARGA ----------
async def show_recharge(update, context):
    _, u = await get_ctx_user(update)
    text = await txt("recharge", id=u[0], saldo=await fmt_brl(u[3] or 0))
    rows = [
        [await btn("recharge_pix", cb="recharge:pix")],
        [await btn("back", cb="nav:welcome")],
    ]
    await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(rows), parse_mode=ParseMode.HTML)

async def ask_recharge_value(update, context):
    text = await get_text("recharge_value_prompt")
    await context.bot.send_message(update.effective_chat.id, text,
        reply_markup=ForceReply(selective=True), parse_mode=ParseMode.HTML)
    context.user_data["await_recharge"] = True

async def handle_recharge_value(update, context):
    if not context.user_data.get("await_recharge"):
        return
    try:
        val = float(update.message.text.replace(",", ".").strip())
    except Exception:
        return await update.message.reply_text("❌ Valor inválido.", reply_to_message_id=update.message.message_id)
    if val < 4:
        return await update.message.reply_text("❌ Valor mínimo: R$ 4,00", reply_to_message_id=update.message.message_id)
    
    context.user_data.pop("await_recharge")
    tg, u = await get_ctx_user(update)
    await start_pix(update, context, u[0], val, "recharge", product_id=None, qty=1)

async def start_pix(update, context, uid, value, type_, product_id=None, qty=1, chat_id=None):
    chat_id = chat_id or update.effective_chat.id
    await context.bot.send_message(chat_id, await get_text("pix_generating"))
    
    # DELAY DE 3 SEGUNDOS AQUI
    await asyncio.sleep(3) 
    
    pix = await payments.create_pix(uid, value)
    ref = pix["ref"]
    code = pix["code"]
    await add_pix(ref, uid, value, type_, code, product_id, qty)
    text = await txt("pix_qr", valor=await fmt_brl(value), id_recarga=ref, codigo_pix=code)
    
    rows = [
        [InlineKeyboardButton(await get_btn("pix_wait"), callback_data=f"pix:check:{ref}")],
        [InlineKeyboardButton(await get_btn("pix_copy"), copy_text=code)],
    ]
    await context.bot.send_message(chat_id, text, reply_markup=InlineKeyboardMarkup(rows), parse_mode=ParseMode.HTML)

# ---------- AFILIADOS ----------
async def show_affiliates(update, context):
    _, u = await get_ctx_user(update)
    a = await get_affiliate(u[0])
    status = a[1]
    comissao = a[2]
    total_ganho = a[3]
    indicacoes = await count_referrals(u[0])
    media = total_ganho / indicacoes if indicacoes else 0
    text = await txt("affiliates",
        status="Ativo" if status == "active" else "Inativo",
        comissao=comissao, indicacoes=indicacoes,
        total_ganho=await fmt_brl(total_ganho),
        media=await fmt_brl(media), saque_minimo="20,00",
        nivel="Bronze", meta="R$ 100,00",
        restantes="R$ " + await fmt_brl(max(0, 100-total_ganho)),
        bot=BOT_USERNAME, id=u[0])
    rows = []
    if status == "active":
        rows.append([await btn("aff_points", cb="aff:points")])
        rows.append([await btn("aff_pdf", cb="aff:pdf")])
    else:
        rows.append([await btn("aff_activate", cb="aff:activate")])
    rows.append([await btn("back", cb="nav:welcome")])
    await update.callback_query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(rows),
        parse_mode=ParseMode.HTML, disable_web_page_preview=True)

# ---------- TOP ----------
async def show_top(update, context, tab="servicos"):
    titles = {"servicos": "SERVIÇOS", "recargas": "RECARGAS", "saldo": "SALDO",
              "gift": "GIFT CARD", "comprar": "COMPRADORES"}
    if tab == "servicos":
        data = await ranking_servicos()
        lista = "\n".join(f"{i+1}º {r[1]} 🥇 — {r[2]} pedidos" for i, r in enumerate(data)) or "—"
    elif tab == "recargas":
        data = await ranking_recargas()
        lista = "\n".join(f"{i+1}º {r[1]} — R$ {await fmt_brl(r[2])}" for i, r in enumerate(data)) or "—"
    elif tab == "saldo":
        data = await ranking_saldo()
        lista = "\n".join(f"{i+1}º {r[1]} — R$ {await fmt_brl(r[2] or 0)}" for i, r in enumerate(data)) or "—"
    elif tab == "gift":
        data = await ranking_gift()
        lista = "\n".join(f"{i+1}º {r[1]} — {r[2]} gifts" for i, r in enumerate(data)) or "—"
    else:
        data = await ranking_servicos()
        lista = "\n".join(f"{i+1}º {r[1]} — {r[2]} compras" for i, r in enumerate(data)) or "—"
    text = await txt("top_ranking", titulo=titles.get(tab, tab.upper()), lista=lista)

    def mk(t):
        label = f"✅ {t.title()}" if t == tab else f"☑️ {t.title()}"
        return InlineKeyboardButton(label, callback_data=f"nav:top:{t}")
    rows = [
        [mk("servicos"), mk("recargas"), mk("saldo")],
        [mk("gift"), mk("comprar")],
        [await btn("back", cb="nav:welcome")],
    ]
    await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(rows), parse_mode=ParseMode.HTML)

# ---------- DEEP LINK VER COMPRA ----------
async def deep_ver_compra(update, context, pid):
    tg = update.effective_user
    h = await has_purchased_product(tg.id, pid)
    if h:
        u = await get_user(tg.id)
        total = await count_user_purchases(u[0], active_only=True)
        items = await user_purchases(u[0], active_only=True, page=0, per_page=1)
        item = items[0]
        p = await get_product(item[2])
        text = await txt("history_item",
            n=f"1/{total}", data=item[7][:10], vencimento=item[8][:10],
            valor=await fmt_brl(item[3]), id_compra=item[0],
            servico=p[2] if p else "—", email=item[4], senha=item[5],
            link=item[6], ref=f"REF{item[0]:06d}")
        rows = [[await btn("back", cb="nav:welcome")]]
        await update.effective_message.reply_text(
            text, reply_markup=InlineKeyboardMarkup(rows), parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    else:
        text = await get_text("access_denied")
        rows = [[InlineKeyboardButton("🛒 Comprar agora", callback_data=f"prod:{pid}")]]
        await update.effective_message.reply_text(
            text, reply_markup=InlineKeyboardMarkup(rows), parse_mode=ParseMode.HTML)

# ---------- INLINE SEARCH ----------
async def inline_search(update, context):
    q = update.inline_query.query.lower().replace("procurar", "").strip()
    prods = await search_products(q) if q else []
    results = []
    for p in prods:
        text = await txt("product",
            produto=p[2], preco=await fmt_brl(p[3]), saldo="0,00",
            estoque=p[5], descricao=p[4] or "—", vendidos=p[6], views=p[7])
        rows = [[InlineKeyboardButton("💳 Comprar", callback_data=f"prod:{p[0]}")]]
        results.append(
            InlineQueryResultArticle(
                id=str(p[0]),
                title=p[2],
                description=f"R$ {await fmt_brl(p[3])}",
                input_message_content=InputTextMessageContent(text, parse_mode=ParseMode.HTML),
                reply_markup=InlineKeyboardMarkup(rows),
            )
        )
    await update.inline_query.answer(results, cache_time=5)

# ---------- CALLBACK ROUTER ----------
async def callback_router(update, context):
    q = update.callback_query
    data = q.data or ""
    await q.answer()
    
    # LIMPA O ESTADO DE INPUT A CADA CLIQUE DE BOTÃO
    context.user_data.pop("await_gift", None)
    context.user_data.pop("await_wa", None)
    context.user_data.pop("await_recharge", None)
    context.user_data.pop("qty_pid", None)

    try:
        if data == "noop":
            return
        if data == "nav:welcome":
            return await send_welcome(update, context, edit=True)
        if data == "nav:catlist:0":
            _, u = await get_ctx_user(update)
            cats = await get_categories()
            text = await txt("catalog", saldo=await fmt_brl(u[3] or 0))
            rows = [[InlineKeyboardButton(f"{c[2]} {c[1]}", callback_data=f"nav:cat:{c[0]}:0")] for c in cats]
            rows.append([await btn("back", cb="nav:welcome")])
            return await q.edit_message_text(text, reply_markup=InlineKeyboardMarkup(rows), parse_mode=ParseMode.HTML)
        if data.startswith("nav:cat:"):
            _, cid, page = data.split(":")
            return await show_category_products(update, context, int(cid), int(page))
        if data.startswith("prod:"):
            pid = int(data.split(":")[1])
            return await show_product(update, context, pid)
        if data.startswith("buy:"):
            pid = int(data.split(":")[1])
            return await do_buy(update, context, pid)
        if data.startswith("buyq:"):
            pid = int(data.split(":")[1])
            return await ask_qty(update, context, pid)
        if data == "nav:profile":
            return await show_profile(update, context)
        if data == "nav:recharge":
            return await show_recharge(update, context)
        if data == "recharge:pix":
            return await ask_recharge_value(update, context)
        if data == "nav:affiliates":
            return await show_affiliates(update, context)
        if data.startswith("nav:top:"):
            return await show_top(update, context, data.split(":")[2])
        if data == "prof:history":
            return await show_history(update, context, page=0, active_only=True)
        if data.startswith("prof:history:"):
            parts = data.split(":")
            if parts[2] == "all":
                return await show_history(update, context, page=0, active_only=False)
            if parts[2] == "active":
                return await show_history(update, context, page=0, active_only=True)
            if parts[2] in ("prev", "next"):
                page = int(parts[3])
                act = bool(int(parts[4]))
                return await show_history(update, context, page=page, active_only=act)
        if data == "prof:gift":
            return await show_gift(update, context)
        if data == "prof:edit":
            return await show_edit_data(update, context)
        if data == "prof:edit:wa":
            return await ask_whatsapp(update, context)
        if data.startswith("pix:buy:"):
            _, _, pid, faltam, qty = data.split(":")
            uid = update.effective_user.id
            return await start_pix(update, context, uid, float(faltam), "purchase", int(pid), int(qty))
        if data.startswith("pix:buymulti:"):
            _, _, pid, qty, faltam = data.split(":")
            uid = update.effective_user.id
            return await start_pix(update, context, uid, float(faltam), "purchase", int(pid), int(qty))
        if data.startswith("pix:check:"):
            return await q.answer("Ainda não identificado. Aguarde...", show_alert=True)
        if data.startswith("dlv:on:"):
            pid = int(data.split(":")[2])
            p = await get_purchase(pid)
            if not p:
                return
            text = await txt("delivery_ok",
                produto="", nome=update.effective_user.full_name, id=update.effective_user.id,
                valor=await fmt_brl(p[3]), email=p[4], senha=p[5], link_acesso=p[6])
            text2 = text.replace("||", "")
            rows = [
                [InlineKeyboardButton(await get_btn("delivery_link"), url=p[6])],
                [InlineKeyboardButton(await get_btn("activate_off"), callback_data="noop")],
            ]
            return await q.edit_message_text(text2, reply_markup=InlineKeyboardMarkup(rows), parse_mode=ParseMode.HTML)
        if data == "aff:activate":
            uid = update.effective_user.id
            await set_affiliate_status(uid, "active")
            return await show_affiliates(update, context)
        if data == "aff:pdf":
            uid = update.effective_user.id
            u = await get_user(uid)
            a = await get_affiliate(uid)
            total_ganho = a[3]
            indicacoes = await count_referrals(uid)
            
            pdf_buf = generate_pdf(uid, u[2], u[1], total_ganho, indicacoes)
            await q.message.reply_document(
                document=pdf_buf,
                filename=f"afiliados_{uid}.pdf",
                caption="📄 <b>Aqui está o seu relatório de afiliados!</b>",
                parse_mode=ParseMode.HTML
            )
            return await q.answer("PDF gerado com sucesso!")
            
        if data == "aff:points":
            uid = update.effective_user.id
            a = await get_affiliate(uid)
            total_ganho = a[3]
            
            if total_ganho <= 0:
                return await q.answer("❌ Você não possui comissões acumuladas para trocar.", show_alert=True)
            
            await add_saldo(uid, total_ganho)
            async with aiosqlite.connect(DATABASE_PATH) as db:
                await db.execute("UPDATE affiliates SET total_earned=0 WHERE user_id=?", (uid,))
                await db.commit()
                
            await q.answer(f"✅ R$ {await fmt_brl(total_ganho)} transferidos para o seu saldo!", show_alert=True)
            return await show_affiliates(update, context)

        if data == "multi:next":
            d = context.user_data["multi"]
            d["idx"] += 1
            return await render_multi(update, context, edit_query=q)
        if data == "multi:prev":
            d = context.user_data["multi"]
            d["idx"] = max(0, d["idx"]-1)
            return await render_multi(update, context, edit_query=q)
    except Exception as e:
        log.exception(f"callback error: {e}")

# ---------- TEXT HANDLER (reply inputs) ----------
async def text_router(update, context):
    if not update.message:
        return
    if context.user_data.get("await_gift"):
        return await handle_gift_code(update, context)
    if context.user_data.get("await_wa"):
        return await handle_whatsapp(update, context)
    if context.user_data.get("await_recharge"):
        return await handle_recharge_value(update, context)
    if context.user_data.get("qty_pid"):
        return await handle_qty_text(update, context)

async def cmd_cancelar(update, context):
    context.user_data.pop("qty_pid", None)
    context.user_data.pop("await_gift", None)
    context.user_data.pop("await_wa", None)
    context.user_data.pop("await_recharge", None)
    await update.message.reply_text("Cancelado.")

# ---------- JOBS ----------
async def job_abandoned(context):
    items = await abandoned_to_notify(minutes=15)
    for a in items:
        uid = a[1]
        pid = a[2]
        type_ = a[3]
        value = a[4]
        try:
            if type_ == "cart":
                p = await get_product(pid)
                if not p:
                    await mark_abandoned_notified(a[0])
                    continue
                text = await txt("abandoned_cart",
                    produto=p[2], preco=await fmt_brl(p[3]), estoque=p[5])
                rows = [
                    [InlineKeyboardButton(await get_btn("abandon_buy"), callback_data=f"prod:{pid}")],
                    [InlineKeyboardButton(await get_btn("abandon_view"), callback_data=f"prod:{pid}")],
                ]
            else:
                text = await txt("abandoned_recharge", valor=await fmt_brl(value))
                rows = [[InlineKeyboardButton("💠 Continuar recarga", callback_data="nav:recharge")]]
            await context.bot.send_message(uid, text, reply_markup=InlineKeyboardMarkup(rows), parse_mode=ParseMode.HTML)
        except Exception as e:
            log.warning(f"abandoned notify: {e}")
        await mark_abandoned_notified(a[0])

async def job_pix_check(context):
    for p in await expired_pix():
        await set_pix_status(p[1], "expired")
        try:
            await context.bot.send_message(
                p[2], await txt("pix_expired", referencia=p[1], valor=await fmt_brl(p[4])),
                parse_mode=ParseMode.HTML)
        except Exception:
            pass
    for p in await pending_pix_older_than(5):
        try:
            await context.bot.send_message(
                p[2], await txt("pix_pending",
                    valor=await fmt_brl(p[4]), id_recarga=p[1], minutos=5),
                parse_mode=ParseMode.HTML)
        except Exception:
            pass

# ---------- BOOTSTRAP ----------
async def post_init(app):
    await init_db()

def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("cancelar", cmd_cancelar))
    app.add_handler(CommandHandler("debug", cmd_debug))
    app.add_handler(ChatMemberHandler(on_chat_member, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(InlineQueryHandler(inline_search))
    app.add_handler(CallbackQueryHandler(callback_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_router))

    app.job_queue.run_repeating(job_abandoned, interval=60, first=30)
    app.job_queue.run_repeating(job_pix_check, interval=60, first=30)

    if WEBHOOK_URL:
        app.run_webhook(
            listen="0.0.0.0", 
            port=PORT, 
            url_path="webhook",
            webhook_url=f"{WEBHOOK_URL}/webhook",
        )
    else:
        app.run_polling()

if __name__ == "__main__":
    main()
