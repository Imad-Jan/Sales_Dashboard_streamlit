import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')
st.set_page_config(page_title="Superstore!!!", page_icon=":bar_chart:",layout="wide")
st.title(" 	:chart: Sales Data Stats")
st.markdown('<style>div.block-container{padding-top:1rem;color:red;}</style>',unsafe_allow_html=True)
df = pd.read_csv("Superstore.csv", encoding="ISO-8859-1")
col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"])

startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()
with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))
with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))
df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()
st.sidebar.header("Choose your filter: ")
region = st.sidebar.multiselect("Pick your Region", df["Region"].unique(), key="0")
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]
state = st.sidebar.multiselect("Pick the State", df2["State"].unique(), key="1")
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]

city = st.sidebar.multiselect("Pick the City",df3["City"].unique(),  key="2")
# Filter the data based on Region, State and City
if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df3[df["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df = df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filtered_df = df3[df["Region"].isin(region) & df3["State"].isin(state)]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
else:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]

category_df = filtered_df.groupby(by = ["Category"], as_index = False)["Sales"].sum()

with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x="Category", y="Sales", text=['${:,.2f}'.format(x) for x in category_df["Sales"]],
                 template="plotly_dark", color="Category")
    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font_color="#262730",
    )
    fig.update_traces(marker=dict(line=dict(color="#262730", width=1)))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    st.plotly_chart(fig, use_container_width=True, height=400)

with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
    fig.update_traces(text=filtered_df["Region"], textposition="outside")
    fig.update_layout(
        template="plotly_dark",
        uniformtext_minsize=12,
        uniformtext_mode="hide",
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font_color="#262730",
    )
    fig.update_traces(marker=dict(line=dict(color="#262730", width=1)))
    st.plotly_chart(fig, use_container_width=True, height=400)
cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Category.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')

with cl2:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by = "Region", as_index = False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap="Oranges"))
        csv = region.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Region.csv", mime = "text/csv",
                        help = 'Click here to download the data as a CSV file')

# Time series Anslysis      
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader('Time Series Analysis')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x = "month_year", y="Sales", labels = {"Sales": "Amount"},height=500, width = 1000,template="gridon")
st.plotly_chart(fig2,use_container_width=True)

with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data = csv, file_name = "TimeSeries.csv", mime ='text/csv')

# Create a treem based on Region, category, sub-Category
st.subheader("Hierarchical view of Sales using Sunburst Chart")
fig3 = px.sunburst(filtered_df, path=["Region", "Category", "Sub-Category"], values="Sales", color="Sub-Category")
fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader('Segment wise Sales')
    fig = px.bar(filtered_df, x="Segment", y="Sales", color="Segment", template="plotly_dark")
    fig.update_layout(title="Segment wise Sales", title_font=dict(size=20),
                      xaxis=dict(title="Segment", title_font=dict(size=19)),
                      yaxis=dict(title="Sales", title_font=dict(size=19)))
    st.plotly_chart(fig, use_container_width=True)
with chart2:
    st.subheader('Category wise Sales')
    fig = px.bar(filtered_df, x="Category", y="Sales", color="Category", template="plotly_dark")
    fig.update_layout(title="Category wise Sales", title_font=dict(size=20),
                      xaxis=dict(title="Category", title_font=dict(size=19)),
                      yaxis=dict(title="Sales", title_font=dict(size=19)))
    st.plotly_chart(fig, use_container_width=True)
import plotly.figure_factory as ff
st.subheader("Month wise Sub-Category Sales Summary")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)
with st.expander("Summary_Table"):
    df_sample = df[0:5][["Region","State","City","Category","Sales","Profit","Quantity"]]
    fig = ff.create_table(df_sample, colorscale = "Cividis")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("Month wise sub-Category Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(data = filtered_df, values = "Sales", index = ["Sub-Category"],columns = "month")
    st.write(sub_category_Year.style.background_gradient(cmap="Blues"))
# Create a bar chart
fig = px.bar(filtered_df, x="Category", y="Sales", color="Sub-Category", barmode="group")
fig.update_layout(title="Sales by Category and Sub-Category", title_font=dict(size=20),
                  xaxis=dict(title="Category", title_font=dict(size=19)),
                  yaxis=dict(title="Sales", title_font=dict(size=19)))
st.plotly_chart(fig, use_container_width=True)

with st.expander("View Data"):
    st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap="Oranges"))
# Download orginal DataSet
csv = df.to_csv(index = False).encode('utf-8')
st.download_button('Download Data', data = csv, file_name = "Data.csv",mime = "text/csv")
st.markdown("-----")

####Customer Section

st.header("Customers Analysis")

top_customers = df.groupby("Customer Name")["Quantity"].sum().reset_index()
top_customers = top_customers.sort_values(by="Quantity", ascending=False).head(10)

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Top Customers")
    st.write("With High Purchase Record")
    st.write(top_customers)  
with col2:
    st.subheader("Top Customers")
    st.write("With High Purchase Record")
    fig = px.bar(top_customers, x="Customer Name", y="Quantity", labels={"Customer Name": "Customer", "Quantity": "Total Quantity"})
    fig.update_layout(xaxis_title="Customer", yaxis_title="Total Quantity")
    st.plotly_chart(fig, use_container_width=True)
with col3:
    st.subheader("Customers by State")
    st.write("Stats with Highest Customer")
    customer_by_state = df.groupby("State")["Customer Name"].nunique().reset_index()
    fig_state = px.pie(customer_by_state, values="Customer Name", names="State", title="Customers by State")
    fig_state.update_traces(textposition='inside', textinfo='percent+label')
    fig_state.update_layout(showlegend=False)
    st.plotly_chart(fig_state, use_container_width=True)
    st.markdown("-----")
#relation chart showing product sales compared to the total number of customers in a state
st.subheader("Product Sales vs. Total Customers by State")
state_sales = df.groupby("State")["Sales"].sum().reset_index()
customer_count_by_state = df.groupby("State")["Customer Name"].nunique().reset_index()
relation_df = pd.merge(state_sales, customer_count_by_state, on="State", suffixes=("_sales", "_customers"))
# Create the relation chart
fig_relation = px.scatter(relation_df, x="Sales", y="Customer Name", text="State",
                          labels={"Sales": "Total Sales", "Customer Name": "Total Customers"},
                          title="Product Sales vs. Total Customers by State")
fig_relation.update_traces(textposition='top center')
st.plotly_chart(fig_relation, use_container_width=True)
st.markdown("-----")



st.header("Product Analysis")
# Products with the most sales
product_sales = df.groupby("Product Name")["Sales"].sum().reset_index()
top_products = product_sales.sort_values(by="Sales", ascending=False).head(10)

# bar chart for the top products
st.subheader("Top Products by Sales (Bar Chart)")
fig_products = px.bar(top_products, x="Sales", y="Product Name",
                      labels={"Sales": "Total Sales", "Product Name": "Product"},
                      title="Top Products by Sales",
                      orientation='h', # Horizontal bar chart
                      color_discrete_sequence=px.colors.qualitative.Set1)  # Beautiful color palette
fig_products.update_layout(yaxis_title="Product", xaxis_title="Total Sales", title_font=dict(size=20))
st.plotly_chart(fig_products, use_container_width=True)
st.markdown("-----")

# Visualize Profit for all products
st.subheader("Profit Analysis")
fig_Profit_margin = px.bar(df, x="Product Name", y="Profit",
                          labels={"Product Name": "Product", "Profit": "Profit (%)"},
                          title="Profit Analysis",
                          color_discrete_sequence=px.colors.qualitative.Set1)
fig_Profit_margin.update_layout(xaxis_title="Product", yaxis_title="Profit (%)", title_font=dict(size=20))
fig_Profit_margin.update_traces(text=["{:.2f}%".format(x) for x in df["Profit"]], textposition='outside')
st.plotly_chart(fig_Profit_margin, use_container_width=True)
st.markdown("-----")

#products with the highest and lowest Profits

highest_Profit_margin_product = df[df['Profit'] == df['Profit'].max()]
lowest_Profit_margin_product = df[df['Profit'] == df['Profit'].min()]
profit, loss = st.columns((2))
with profit: 
        st.write("Highest Profit Product:")
        st.write(highest_Profit_margin_product[["Product Name", "Profit"]])
with  loss:
        st.write("Lowest Profit Product:")
        st.write(lowest_Profit_margin_product[["Product Name", "Profit"]])
