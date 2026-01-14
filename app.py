import streamlit as st
import pandas as pd
import numpy as np

# --- 頁面設定 ---
st.set_page_config(page_title="薇薇安的資產儀表板 Pro", layout="wide", page_icon="💎")

# --- CSS樣式 (維持 Percento 極簡風) ---
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    div[data-testid="stMetricValue"] { font-size: 24px; color: #31333F; }
    .big-header { font-size: 20px; font-weight: bold; color: #FF4B4B; }
</style>
""", unsafe_allow_html=True)

# --- 標題 ---
st.title("💎 薇薇安的資產領航員 V2.0")
st.markdown("### 資金流向一目瞭然：公私分明、精準記帳")

# --- 側邊欄：參數設定 ---
st.sidebar.header("⚙️ 環境參數")
usd_rate = st.sidebar.number_input("美金匯率 (USD/TWD)", value=32.5, step=0.1)
loan_rate = st.sidebar.slider("信貸年利率 (%)", 1.0, 15.0, 3.5, step=0.1)
stock_growth = st.sidebar.slider("預估股票年化報酬率 (%)", -10.0, 20.0, 6.0, step=0.5)

# ==========================================
# 第一區：股票投資 (生錢的鵝)
# ==========================================
st.subheader("1. 股票與基金部位")

col1, col2, col3 = st.columns(3)
with col1:
    st.info("🇹🇼 0050 (台股)")
    stock_0050_cost = 2961
    stock_0050_value = st.number_input("0050 目前市值 (TWD)", value=2961)

with col2:
    st.info("🇺🇸 QQQM (美股)")
    stock_qqqm_value_usd = st.number_input("QQQM 目前市值 (USD)", value=0.0)
    stock_qqqm_value_twd = stock_qqqm_value_usd * usd_rate
    st.caption(f"折合台幣: ${stock_qqqm_value_twd:,.0f}")

with col3:
    st.info("🇺🇸 VTI (定期定額)")
    stock_vti_cost = 5058
    stock_vti_value_usd = st.number_input("VTI 目前市值 (USD)", value=160.0)
    stock_vti_value_twd = stock_vti_value_usd * usd_rate
    st.caption(f"折合台幣: ${stock_vti_value_twd:,.0f}")

# 自選 5 個格子
st.write("📈 **自選台股部位 (填入市值)**")
df_custom = pd.DataFrame(
    [
        {"代號/名稱": "自選股 1", "目前市值": 0},
        {"代號/名稱": "自選股 2", "目前市值": 0},
        {"代號/名稱": "自選股 3", "目前市值": 0},
        {"代號/名稱": "自選股 4", "目前市值": 0},
        {"代號/名稱": "自選股 5", "目前市值": 0},
    ]
)
edited_df = st.data_editor(df_custom, num_rows="fixed", hide_index=True, use_container_width=True)
custom_stock_total = edited_df["目前市值"].sum()

# ==========================================
# 第二區：現金、雜項資產與公款 (關鍵新增)
# ==========================================
st.subheader("2. 銀行現金 & 其他資產")

c1, c2, c3 = st.columns(3)

with c1:
    st.success("💰 銀行總餘額 (看到的錢)")
    # 這裡讓妳填戶頭看到的「總數字」，不用自己先扣掉公款
    cash_bank_total = st.number_input("所有銀行戶頭總現金", value=1369541, help="把合庫、證券戶、手邊現金全部加總填進來")
    
with c2:
    st.warning("📦 隱藏資產 (變現價值)")
    insurance_value = st.number_input("保單目前解約金/價值", value=0, help="如果現在解約可以拿回多少錢？或是儲蓄險目前價值")
    inventory_value = st.number_input("現有庫存貨品價值", value=0, help="妳囤的貨如果賣掉大概值多少成本價")

with c3:
    st.error("🚫 暫存公款 (不屬於妳的錢)")
    client_funds = st.number_input("帳戶內的客戶貨款/代收款", value=0, help="這筆錢在戶頭裡，但之後要繳給廠商或公司的")
    
# ==========================================
# 第三區：長期負債
# ==========================================
st.subheader("3. 負債管理")
d1, d2 = st.columns([1, 2])
with d1:
    debt_loan = st.number_input("信貸/貸款 剩餘本金", value=1950000)
    monthly_pay = 26550
with d2:
    st.info("💡 貼心提醒")
    st.markdown(f"每月還款 **${monthly_pay:,}**。系統會自動幫妳計算一年後還掉多少本金。")

# ==========================================
# 計算核心邏輯
# ==========================================

# 1. 總資產 (Total Assets) = 股票 + 銀行現金 + 保單 + 囤貨
total_stock = stock_0050_value + stock_qqqm_value_twd + stock_vti_value_twd + custom_stock_total
total_other_assets = insurance_value + inventory_value
# 注意：這裡的總資產我們算「帳面總資產」，稍後在淨值扣除公款
gross_assets = total_stock + cash_bank_total + total_other_assets

# 2. 總負債 (Total Liabilities) = 信貸 + 暫存公款
total_liabilities = debt_loan + client_funds

# 3. 淨資產 (Net Worth) = 真正屬於妳的錢
net_worth = gross_assets - total_liabilities

# ==========================================
# 顯示儀表板
# ==========================================
st.divider()
st.markdown("## 📊 薇薇安的財務快照")

m1, m2, m3, m4 = st.columns(4)
m1.metric("1. 股票與基金", f"${total_stock:,.0f}")
m2.metric("2. 可用現金+囤貨+保單", f"${(cash_bank_total + total_other_assets - client_funds):,.0f}", help="已扣除暫存公款，這是妳真正能動用的資源")
m3.metric("3. 總負債 (含公款)", f"${total_liabilities:,.0f}", delta_color="inverse")
m4.metric("🏆 淨資產 (身價)", f"${net_worth:,.0f}", delta=f"資產負債比: {total_liabilities/gross_assets*100:.1f}%")

if client_funds > 0:
    st.caption(f"⚠️ 注意：妳的銀行餘額中有 **${client_funds:,.0f}** 是客戶的錢，系統已在淨值中自動扣除。")

# ==========================================
# 一年後預測 (Pro 版邏輯)
# ==========================================
st.divider()
st.subheader("🔮 穿越時空：一年後的變化")

# 計算邏輯：
# 1. 股票成長
projected_stock = total_stock * (1 + stock_growth/100)
monthly_invest_vti = 160 * usd_rate
projected_new_vti = (monthly_invest_vti * 12) * (1 + stock_growth/100/2) # 簡單估算
final_stock = projected_stock + projected_new_vti

# 2. 負債攤還
yearly_pay = monthly_pay * 12
interest_expense = debt_loan * (loan_rate / 100)
principal_paid = yearly_pay - interest_expense
final_loan = debt_loan - principal_paid

# 3. 資產變化
# 假設保單和庫存價值不變 (或妳可以自己加成長率)
# 假設「客戶貨款」是流動的，年底還是保持差不多水位，不影響淨值變化，只影響現金水位
# 現金流出 = 還債 + 買VTI
cash_outflow = yearly_pay + (monthly_invest_vti * 12)
final_cash = cash_bank_total - cash_outflow

# 4. 最終淨值
final_assets = final_stock + final_cash + total_other_assets
final_liabilities = final_loan + client_funds
final_net_worth = final_assets - final_liabilities
wealth_change = final_net_worth - net_worth

# 顯示預測
c_final_1, c_final_2 = st.columns(2)

with c_final_1:
    st.write(f"### 一年後預估身價： :green[${final_net_worth:,.0f}]")
    st.success(f"🎉 妳的資產將增加： **${wealth_change:,.0f}**")
    
    st.markdown("#### 變化細節：")
    st.write(f"- 📈 股票增值(含新投入): +${(final_stock - total_stock):,.0f}")
    st.write(f"- 📉 成功償還本金: +${principal_paid:,.0f}")
    st.write(f"- 💸 扣除利息支出: -${interest_expense:,.0f}")

with c_final_2:
    # 簡單圖表
    chart_data = pd.DataFrame({
        "時間": ["現在", "一年後"],
        "淨資產": [net_worth, final_net_worth],
        "負債": [total_liabilities, final_liabilities]
    })
    st.bar_chart(chart_data.set_index("時間"))
