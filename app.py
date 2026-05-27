import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Uber Analytics",
                   layout="wide",
                   page_icon="🏎️")

df = pd.read_csv("Uber data set ncr.xlsx - ncr_ride_bookings.csv")

# sidebar
with st.sidebar:
    selected = option_menu(
        menu_title="Main Menu",
        options=["Dataset", "Overview", "Ride Analytics","Data Assistant"],
        icons=["table", "bar-chart", "graph-up","robot"],
        menu_icon="car-front",
        default_index=0
    )

# dataset
if selected == "Dataset":
    st.title("Data Exploration")

    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Rows", value=df.shape[0])
    col2.metric(label="Total Columns", value=df.shape[1])
    col3.metric(label="Missing Values", value=df.isnull().sum().sum())

    st.divider()

    # column selection
    st.subheader("Select Columns")
    selected_columns = st.multiselect(
        label="Choose Columns",
        options=df.columns,
        default=df.columns
    )
    filtered_df = df[selected_columns]

    st.divider()

    # search dataset
    st.subheader("Search in Dataset")
    search = st.text_input("Search Data From Here")

    if search:
        filtered_df = filtered_df[
            filtered_df.astype(str).apply(
                lambda row: row.str.contains(search, case=False).any(),axis=1
            )]
    st.divider()

    #column filter -column name|value
    st.subheader("Select Columns")
    col1,col2=st.columns(2)
    with col1:
        filter_column=st.selectbox("Select Column",filtered_df.columns)
    with col2:
        filter_value =st.selectbox("Select Value",filtered_df[filter_column].dropna().unique())

    st.divider()
    st.dataframe(filtered_df)
    st.markdown("### Download Here ")
    csv = filtered_df.to_csv(index=False).encode('UTF-8')
    st.download_button(label="Download",
                       data=csv,
                       file_name="Thai_gyu.csv",
                       mime="text/csv")
    st.divider()
    #slider
    st.subheader("Row slider")
    row_num=st.slider("Select Row Number",0,max_value=df.shape[0])

    st.subheader("Row Preview")
    st.dataframe(filtered_df.iloc[row_num-1])

#----------------------- Overview-------------------------------

if selected == "Overview":
    st.title("Dashboard Overview")
    col1, col2 = st.columns(2)
    col1.metric("Total Rides",len(df))
    col2.metric("Revenue",df["Booking Value"].sum())
    st.divider()



    total_revenue=df["Booking Value"].sum()
    total_ride=len(df)

    # business unit performance
    st.subheader("Business Unit Performance")
    bu_metrix =df.groupby("Vehicle Type").agg(
        Total_Booking=("Booking ID","count"),
        Revenue_Generated=("Booking Value","sum"),
        Avg_Distance=("Ride Distance","mean"),
        Av_Rating=("Customer Rating","mean"),
    )
    bu_metrix["Revenue Share%"]=(bu_metrix["Revenue_Generated"]/total_revenue*100
                                 if total_revenue>0 else 0)
    st.dataframe(bu_metrix.style.format({
        "Total_Booking":"${:,.2f}",
        "Avg_Distance":"{:,.2f}km",
        "Av_Rating":"{:,.2f}%",
        "Revenue_Generated":"{:,.2f}%",
        "Revenue_Share%":"{:,.2f}%"
    }).background_gradient(subset="Revenue_Generated",cmap="RdYlGn"))

    # operation efficiency
    col_eff,col_can = st.columns(2)
    with col_eff:
        st.subheader("operation efficiency")
        eff_df=df.groupby("Vehicle Type")[["Avg VTAT","Avg CTAT"]].mean()
        st.write("Average Turn Around Time (In Minutes)")
        st.dataframe(eff_df.style.highlight_max(axis=0,color="#d81416").highlight_min(axis=0,color="#e6ed6f")
                     ,use_container_width=True )

    with col_can:
        st.subheader("Cancellation Audit")
        status_count = df["Booking Status"].value_counts().to_frame(name="Count")
        status_count["Share %"]=(status_count["Count"]/total_ride*100)
        st.dataframe(status_count,use_container_width=True )

    # FINANCIAL DEEP DIVE
    st.header("Financial Deep Dive")
    pay_col, reason_col = st.columns([4, 6])

    # payment analysis
    # Completed rides count
    completed_ride = (df["Booking Status"] == "Completed").sum()

    with pay_col:
        st.markdown("### 💳 Payment Method Overview")

        pay_summary = (
                df["Payment Method"]
                .fillna("Unknown")
                .value_counts(normalize=True)
                * 100
        ).round(2).reset_index()

        pay_summary.columns = ["Payment Method", "% Usage"]

        st.dataframe(pay_summary, use_container_width=True)



    with reason_col:
        st.markdown("**Primary Cancellation Trigger")

        cust_reason = (df["Reason for cancelling by Customer"]
                       .dropna()
                       .value_counts()
                       .head(3))

        drv_reason = (df["Driver Cancellation Reason"]
                      .dropna()
                      .value_counts()
                      .head(3))

        cust_reason.index = "Customer:" + cust_reason.index
        drv_reason.index = "Driver:" + drv_reason.index

        reason_df = pd.concat([cust_reason, drv_reason]).to_frame()
        reason_df.columns = ["Incident Found"]

        st.dataframe(reason_df)


    # Data Quality

    with st.expander("Data Quality & Audit Logs"):
        audit1,audit2 = st.columns(2)
        audit1.write(f"Duplicate Records :{df.duplicated().sum()}")
        audit2.write(f"Missing Value :{df["Booking Value"].isna().sum()}")
        st.info("Missing Booking value are Expected for Cancelled ride or no-driver found")
        st.success("Executive Overview Generated from Operational Dataset")

    st.title("Uber Operation")
    st.markdown("---")


    # strategic kpi layer

    completed_ride=df[df["Booking Status"]=="Completed"]
    total_revenue=completed_ride["Booking Value"].sum()
    avg_distance=completed_ride["Ride Distance"].mean()
    success_rate=(len(completed_ride)/total_ride*100 if total_ride>0 else 0)
    avg_rating = completed_ride["Customer Rating"].dropna().mean()

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Gross Total Revenue",
                f"{total_revenue:,.0f}",
                "Target:%1.2M")

    kpi2.metric("Fulfilment Rate",
                f"{success_rate:,.1f}",
                "-2.4% vs Last Month",
                "red")

    kpi3.metric("Avg Distance",
                f"{avg_distance:,.2f}km")

    kpi4.metric("Avg Rating",
                f"{avg_rating:.1f}")

    # show full dataset

    if st.checkbox("Show Full Dataset"):
        st.dataframe(completed_ride,use_container_width=True )

    # Column statics

    st.subheader("Column Statistics")
    numeric_cols=df.select_dtypes(include=["int64", "float64"]).columns

    if len(numeric_cols)>0:
        selected_columns=st.selectbox("Select Numeric Value",numeric_cols)
        st.write(df[selected_columns].describe())
    st.divider()

# ------------------------------- Ride Analytics -----------------------------------------

if selected == "Ride Analytics":
    st.title("Advance Ride Intelligence Dashboard")
    st.divider()

    completed = df[df["Booking Status"]=="Completed"]


    # sunburst chart

    st.subheader("Revenue Hierarchy")
    fig1=px.sunburst(completed,path=["Vehicle Type","Payment Method"],
                     values="Booking Value",
                     color="Booking Value",
                     color_continuous_scale="Turbo"
                     )
    fig1.update_layout(height=500)
    st.plotly_chart(fig1)
    st.divider()

    # Treemap

    st.subheader("Revenue Distribution")

    fig2=px.treemap(completed,path=["Vehicle Type","Payment Method"],
                    values="Booking Value",
                    color="Booking Value",
                    color_continuous_scale="Blues"
                    )
    fig2.update_layout(margin=dict(t=20,l=0,r=0,b=0),height=420)
    st.plotly_chart(fig2,use_container_width=True )
    st.divider()


    st.subheader("Customer Rating Spread")
    fig3=px.box(completed,
                x="Vehicle Type",
                y="Customer Rating",
                color="Vehicle Type")
    fig3.update_layout(showlegend=True,height=420)
    st.plotly_chart(fig3)
    st.divider()

    # SANKEY CHART

    st.subheader("Ride Flow Analysis")
    flow=df.groupby(["Vehicle Type","Booking Status"]).size().reset_index(name="count")
    source_label=flow["Vehicle Type"].unique().tolist()
    target_label=flow["Booking Status"].unique().tolist()

    labels= source_label + target_label

    source = flow["Vehicle Type"].apply(
        lambda x : labels.index(x)
    )

    target = flow["Booking Status"].apply(
        lambda x : labels.index(x)
    )

    value = flow["count"].tolist()

    import plotly.graph_objects as go


    fig4 =go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="blue",width=0.5),label=labels
        ),
        link=dict(
            source=source,
            target=target,
            value=value
        )
    )])
    fig4.update_layout(height=500)
    st.plotly_chart(fig4)
    st.divider()

    # BAR CHART

    st.subheader("1. Ride Demand by Vehicle Type")
    ride_demand = df["Vehicle Type"].value_counts().reset_index()
    ride_demand.columns = ["Vehicle Type", "Total Bookings"]

    fig5 = px.bar(ride_demand,
                  x="Vehicle Type",
                  y="Total Bookings",
                  color="Vehicle Type")
    st.plotly_chart(fig5,use_container_width=True )
    st.divider()

    # Horizontal Bar Chart

    st.subheader("2. Revenue by Vehicle Type")
    df = df.dropna(subset=["Vehicle Type", "Booking Value"])
    revenue_data = df.groupby("Vehicle Type")["Booking Value"].sum().reset_index(name="Total Booking Value")
    fig = px.bar(
        revenue_data,
        x="Total Booking Value",
        y="Vehicle Type",
        color="Vehicle Type",
        orientation="h"
    )

    st.plotly_chart(fig, use_container_width=True)
    st.divider()


    st.subheader("3. Booking Status Distribution")
    df = df.dropna(subset=["Booking Status"])
    status_data = df["Booking Status"].value_counts().reset_index(name="Ride Count")

    fig = px.pie(
        status_data,
        names="Booking Status",
        values="Ride Count",
        hole=0.4,
        title="Booking Status Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)
    st.divider()


    # Donut Chart
    st.subheader("4. Payment Method Usage")
    status_data = df["Payment Method"].value_counts().reset_index(name="Usage %")

    fig = px.pie(
        status_data,
        names="Payment Method",
        values="Usage %",
        title="Revenue by Payment Method"
    )

    st.plotly_chart(fig, use_container_width=True)
    st.divider()


    st.subheader("5. Ride Distance vs Booking Value")
    clean_df = df.dropna(subset=["Ride Distance", "Booking Value"])
    fig=px.scatter(clean_df,
        x="Ride Distance",
        y="Booking Value",
        color="Vehicle Type",
    )
    fig.update_xaxes(showgrid=True,gridcolor="red")
    fig.update_yaxes(showgrid=True,gridcolor="red")
    st.plotly_chart(fig,theme=None)
    st.divider()


    # histogram
    st.subheader("6. Customer Rating Distribution")
    clean_df=df.dropna(subset=["Customer Rating"])
    fig =px.histogram(clean_df,x="Customer Rating",
                      nbins=10)
    fig.update_layout(
        xaxis_title="Customer Rating",
        yaxis_title="Frequency"
    )
    st.plotly_chart(fig)
    st.divider()



    st.subheader("7. Cancellation Reasons Analysis")
    cancel_data = df["Booking Status"].value_counts().reset_index(name="Count")

    fig = px.bar(
        cancel_data,
        x="Count",
        y="Booking Status",
        orientation="h"
    )

    st.plotly_chart(fig, use_container_width=True)
    st.divider()


    st.subheader("8. Average Distance by Vehicle Type")
    clean_df=df.dropna(subset=["Vehicle Type","Ride Distance"])
    avg_data = clean_df.groupby("Vehicle Type")["Ride Distance"].mean().reset_index(name="Average Ride Distance")
    fig=px.bar(avg_data,
               x="Vehicle Type",
               y="Average Ride Distance",
               color="Vehicle Type"
               )
    st.plotly_chart(fig, use_container_width=True)
    st.divider()


    st.subheader("9. Booking Value Distribution")
    clean_df=df.dropna(subset=["Booking Value"])
    fig =px.histogram(clean_df,x="Booking Value",
                      nbins=20)
    fig.update_layout(
        xaxis_title="Booking Value",
        yaxis_title="Frequency"
    )
    st.plotly_chart(fig)
    st.divider()



    st.subheader("10. Operational Efficiency (CTAT vs VTAT)")
    clean_df = df.dropna(subset=["Avg CTAT", "Avg VTAT"])
    fig = px.scatter(clean_df,
                     x="Avg CTAT",
                     y="Avg VTAT",
                     color="Vehicle Type",
                     )
    fig.update_xaxes(showgrid=True, gridcolor="red")
    fig.update_yaxes(showgrid=True, gridcolor="red")
    st.plotly_chart(fig, theme=None)
    st.divider()

# -------------------------- Data Assistant -------------------------------
if selected=="Data Assistant":
    st.title("Data Assistant")
    st.divider()

    st.write("Ask Questions about the dataset and get visual analytics")
    user_question =st.text_input("Enter your question")

    if user_question:
        q = user_question.lower()

        completed = df[df["Booking Status"]=="Completed"]

        # total rides

        if "total rides" in q:
            total = len(df)
            st.success(f"Total Ride in Dataset: {total}")

            status = df["Booking Status"].value_counts()
            fig = px.bar(x=status.index,
                         y=status.values,
                         labels={"x":"Booking Status","y":"Ride Count"},
                         title="Ride distribution by status")
            st.plotly_chart(fig, use_container_width=True)


        # revenue analysis

        elif "revenue" in q:
            revenue = completed.groupby("Vehicle Type")["Booking Value"].sum()
            st.success(f"Total Revenue{revenue.sum():,.2f}")

            fig = px.bar(x=revenue.index,
                         y=revenue.values,
                         title="Revenue by Vehicle Type",
                         labels={"x":"Vehicle Type","y":"Booking Value"})
            st.plotly_chart(fig, use_container_width=True)


        # vehicle

        elif "vehicle" in q:
            vehicle = df["Vehicle Type"].value_counts()
            st.success(f"Most Used Vehicle: {vehicle.idxmax()}")
            fig = px.pie(names=vehicle.index,
                         values=vehicle.values,
                         title="Vehicle Usage Distribution")
            st.plotly_chart(fig)

        # Payment

        elif "payment" in q:
            payment= df["Vehicle Type"].value_counts()
            fig = px.pie(names=payment.index,
                         values=payment.values,
                         title="Payment Usage Distribution")
            st.plotly_chart(fig)

        # cancellation

        elif "cancel" in q :
            cancel = df["Booking Status"].value_counts()
            fig = px.bar(x=cancel.index,
                         y=cancel.values,
                         title="Ride Status",
                         labels={"x":"Booking Status","y":"Ride Count"})
            st.plotly_chart(fig)

        # Rating

        elif "rating" in q:
            fig = px.histogram(completed,
                               x="Customer Rating",
                               nbins=10,
                               title="Customer Rating")
            st.plotly_chart(fig)
            st.success(f"Average Rating{completed["Customer Rating"].mean():,.1f}")


        # distance analytics

        elif "distance" in q:
            fig = px.scatter(completed,
                             x="Ride Distance",
                             y="Booking Value",
                             title="Ride Distance VS Booking Value",
                             color="Vehicle Type"
                             )
            st.plotly_chart(fig)
            st.success(f"Average Distance{completed["Ride Distance"].mean():,.2f}km")

        else:
            st.warning("Question not recognized please ask questions from cancellation ,vehicle,revenue etc")