import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
from dash.dependencies import Input, Output
import plotly.express as px
import datetime
from datetime import date
import re

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
#app = dash.Dash(__name__) #initalize dash app
server = app.server #this line will only be used by Heroku server and not used on local
app.title = "ETM Daily Summary" #Assigning title to be displayed on tab

#Reading the dataset
#tkd = pd.read_csv("C_Ticketdetails_ETM.csv")
#tkd = pd.read_csv("C_Ticketdetails_ETM.csv",parse_dates=['Date'])
tkd = pd.read_csv("Ticketdetails_ETM_20210805_1749.csv")
#creating two seperate columns for date and time
tkd["issuedatetime"]=pd.to_datetime(tkd.issuedatetime)
tkd["Date"]=tkd["issuedatetime"].dt.date
tkd["Time"]=tkd["issuedatetime"].dt.time

tpd = pd.read_csv("Trips_ETM_20210805_1748.csv")
bt = pd.read_excel("Bus-Kandy.xlsx")

#use merge function to tpd & bt
tpmb = pd.merge(tpd,bt,on="busregno",how="left")

#merge tickets,trips,bus details
mdf = pd.merge(tkd,tpmb,on="posticketid",how="left")

#Layout codes
app.layout = dbc.Container(
    [#Title
     dbc.Alert("Daily Summary Report",
               color="dark",
               style={"textAlign":"center","fontSize":20,"fontWeight":"bold"}
               ),
     #1st part
     #dcc.Input(id="my_input",value="2021-07-30"),
     dcc.DatePickerSingle(
        id="my_input",
        min_date_allowed=date(1995, 1, 1),
        initial_visible_month=date(2021,7,30),
        persistence=False,
        first_day_of_week=1,
        placeholder="Select Date:",
        reopen_calendar_on_clear=True,
        show_outside_days=False
        ),
     dbc.Card(dbc.ListGroup(
        [dbc.ListGroupItem(id="selected_day"),
         dbc.ListGroupItem(id="ticket_machines&busses"),
         dbc.ListGroupItem(id="total_income"),
         dbc.ListGroupItem(id="total_no_of_trips"),
         dbc.ListGroupItem(id="total_no_of_passengers"),
         dbc.ListGroupItem(id="ave_income_per_trip"),
         dbc.ListGroupItem(id="ave_income_per_passenger"),
        ],
        flush=False,
        ),
        style={"fontSize":12,
               "width":400,
               "border":"2px solid powderblue",
               'padding':'2px',
               "display":"inline-block"}),
     #2nd part - Route Income Table
     dbc.Table([
         html.Tr([html.Th(""),html.Th("Route",style={"color":"blue","textAlign":"center","fontFamily":"Couier"}),html.Th("Corridor"),html.Th("Income"),html.Th("As a % of total income")]),
         html.Tr([html.Th("Highest Income Route"),html.Td(id="highest_ri_route"),html.Td(id="highest_ri_corridor"),html.Td(id="highest_ri"),html.Td(id="hpercentage_of_ri")]),
         html.Tr([html.Th("Lowest Income Route"),html.Td(id="lowest_ri_route"),html.Td(id="lowest_ri_corridor"),html.Td(id="lowest_ri"),html.Td(id="lpercentage_of_ri")]),
         ], bordered=True, size="sm", style={"margin":"20px","fontSize":12,"width":900,"border":"2px solid powderblue"}
         ),
     #3rd part - Route Demand Table
     dbc.Table([
         html.Tr([html.Th(""),html.Th("Route"),html.Th("Corridor"),html.Th("Passengers"),html.Th("As a % of total passengers")]),
         html.Tr([html.Th("Highest Demand Route"),html.Td(id="highest_rd_route"),html.Td(id="highest_rd_corridor"),html.Td(id="highest_rd"),html.Td(id="hpercentage_of_rd")]),
         html.Tr([html.Th("Lowest Demand Route"),html.Td(id="lowest_rd_route"),html.Td(id="lowest_rd_corridor"),html.Td(id="lowest_rd"),html.Td(id="lpercentage_of_rd")]),
         ],striped=True,bordered=True,hover=True,size="sm",style={"margin":"20px","fontSize":12,"width":900,"border":"2px solid powderblue"}
         ),
     #4th part - Bus Income Table
     dbc.Table([
         html.Tr([html.Th(""),html.Th("Bus Reg. No."),html.Th("Route"),html.Th("Corridor"),html.Th("Income"),html.Th("As a % of total income")]),
         html.Tr([html.Th("Highest Income Bus"),html.Td(id="highest_bi_bus"),html.Td(id="highest_bi_route"),html.Td(id="highest_bi_corridor"),html.Td(id="highest_bi"),html.Td(id="hpercentage_of_bi")]),
         html.Tr([html.Th("Lowest Income Bus"),html.Td(id="lowest_bi_bus"),html.Td(id="lowest_bi_route"),html.Td(id="lowest_bi_corridor"),html.Td(id="lowest_bi"),html.Td(id="lpercentage_of_bi")]),
         ],striped=True,bordered=True,hover=True,size="sm",style={"margin":"20px","fontSize":12,"width":900,"border":"2px solid powderblue"}
         ),
     #Plot 
     dcc.Graph(id="liner_plot",
               figure=dict(layout=dict(title="Daily Income Variance"),
               style={"width":"50%"},
               responsive=True)
               )
     ]
)
     
@app.callback(
    #1st part
    Output(component_id="selected_day",component_property="children"),
    Output(component_id="ticket_machines&busses",component_property="children"),
    Output(component_id="total_income",component_property="children"),
    Output(component_id="total_no_of_trips",component_property="children"),
    Output(component_id="total_no_of_passengers",component_property="children"),
    Output(component_id="ave_income_per_trip",component_property="children"),
    Output(component_id="ave_income_per_passenger",component_property="children"),
    #2nd part
    Output(component_id="highest_ri_route",component_property="children"),
    Output(component_id="lowest_ri_route",component_property="children"),
    Output(component_id="highest_ri_corridor",component_property="children"),
    Output(component_id="lowest_ri_corridor",component_property="children"),
    Output(component_id="highest_ri",component_property="children"),
    Output(component_id="lowest_ri",component_property="children"),
    Output(component_id="hpercentage_of_ri",component_property="children"),
    Output(component_id="lpercentage_of_ri",component_property="children"),
    #3rd part
    Output(component_id="highest_rd_route",component_property="children"),
    Output(component_id="lowest_rd_route",component_property="children"),
    Output(component_id="highest_rd_corridor",component_property="children"),
    Output(component_id="lowest_rd_corridor",component_property="children"),
    Output(component_id="highest_rd",component_property="children"),
    Output(component_id="lowest_rd",component_property="children"),
    Output(component_id="hpercentage_of_rd",component_property="children"),
    Output(component_id="lpercentage_of_rd",component_property="children"),
    #4th part
    Output(component_id="highest_bi_bus",component_property="children"),
    Output(component_id="lowest_bi_bus",component_property="children"),
    Output(component_id="highest_bi_route",component_property="children"),
    Output(component_id="lowest_bi_route",component_property="children"),
    Output(component_id="highest_bi_corridor",component_property="children"),
    Output(component_id="lowest_bi_corridor",component_property="children"),
    Output(component_id="highest_bi",component_property="children"),
    Output(component_id="lowest_bi",component_property="children"),
    Output(component_id="hpercentage_of_bi",component_property="children"),
    Output(component_id="lpercentage_of_bi",component_property="children"),
    #Plot
    Output("liner_plot","figure"),
    Input("my_input","date"),
    )

def filtering_day(day):
    #filtered data rows
    fd = mdf[mdf["Date"] == datetime.datetime.strptime(day,"%Y-%m-%d").date()]
    #first part
    total_income = fd["amount"].sum()
    total_no_of_trips = fd["posticketid"].nunique(dropna=True)
    total_no_of_passengers = fd["nooftickets"].sum()
    ave_income_per_trip = total_income/total_no_of_trips
    ave_income_per_passenger = total_income/total_no_of_passengers
    no_of_ticketingmachines_used = fd["posid"].nunique(dropna=True)
    no_of_busses_operated = fd["busregno"].nunique(dropna=False)
    #second part - Routes income
    #Highest
    ri = fd.pivot_table(index="routeid",values="amount",aggfunc='sum')
    highest_ri = ri["amount"].max()
    highest_ri_routeid = ri["amount"].idxmax()
    highest_ri_route = fd.loc[fd["routeid"]==highest_ri_routeid,"Route"].iloc[0]
    highest_ri_corridor = fd.loc[fd["routeid"]==highest_ri_routeid,"Corridor"].iloc[0]
    hpercentage_of_ri = (highest_ri/total_income)*100
    #Lowest
    lowest_ri = ri["amount"].min()
    lowest_ri_routeid = ri["amount"].idxmin()
    lowest_ri_route = fd.loc[fd["routeid"]==lowest_ri_routeid,"Route"].iloc[0]
    lowest_ri_corridor = fd.loc[fd["routeid"]==lowest_ri_routeid,"Corridor"].iloc[0]
    lpercentage_of_ri = (lowest_ri/total_income)*100
    #third part - Route demand
    #Highest
    rd = fd.pivot_table(index="routeid",values="nooftickets",aggfunc='sum')
    highest_rd = rd["nooftickets"].max()
    highest_rd_routeid = rd["nooftickets"].idxmax()
    highest_rd_route = fd.loc[fd["routeid"]==highest_rd_routeid,"Route"].iloc[0]
    highest_rd_corridor = fd.loc[fd["routeid"]==highest_rd_routeid,"Corridor"].iloc[0]
    hpercentage_of_rd = (highest_rd/total_no_of_passengers)*100
    #Lowest
    lowest_rd = rd["nooftickets"].min()
    lowest_rd_routeid = rd["nooftickets"].idxmin()
    lowest_rd_route = fd.loc[fd["routeid"]==lowest_rd_routeid,"Route"].iloc[0]
    lowest_rd_corridor = fd.loc[fd["routeid"]==lowest_rd_routeid,"Corridor"].iloc[0]
    lpercentage_of_rd = (lowest_rd/total_no_of_passengers)*100
    #forth part - Bus income
    #Highest
    bi = fd.pivot_table(index="busregno",values="amount",aggfunc='sum')
    highest_bi = bi["amount"].max()
    highest_bi_bus = bi["amount"].idxmax()
    highest_bi_route = fd.loc[fd["busregno"]==highest_bi_bus,"Route"].iloc[0]
    highest_bi_corridor = fd.loc[fd["busregno"]==highest_bi_bus,"Corridor"].iloc[0]
    hpercentage_of_bi = (highest_bi/total_income)*100
    #Lowest
    lowest_bi = bi["amount"].min()
    lowest_bi_bus = bi["amount"].idxmin()
    lowest_bi_route = fd.loc[fd["busregno"]==lowest_bi_bus,"Route"].iloc[0]
    lowest_bi_corridor = fd.loc[fd["busregno"]==lowest_bi_bus,"Corridor"].iloc[0]
    lpercentage_of_bi = (lowest_bi/total_income)*100
    #plot
    liner_graph = mdf.pivot_table(index="Date",values="amount",aggfunc="sum")
    fig = px.line(liner_graph, x=liner_graph.index, y="amount",title="Daily Income Variance")

    return (
            #1st part
            "Selected Day:  {}".format(day), 
            "No. of ticket machines used:  "+str(no_of_ticketingmachines_used)+" & No. of busses operated:  "+str(no_of_busses_operated), 
            "Total Income: Rs.  "+str(total_income),
            "Total No. of Trips:  "+str(total_no_of_trips),
            "Total No. of Passengers:  "+str(total_no_of_passengers),
            "Ave. income per trip:  "+str(ave_income_per_trip),
            "Ave. income per passenger:  "+str(ave_income_per_passenger),
            #2nd part
            highest_ri_route,
            lowest_ri_route,
            highest_ri_corridor,
            lowest_ri_corridor,
            "Rs. "+str(highest_ri),
            "Rs. "+str(lowest_ri),
            hpercentage_of_ri,
            lpercentage_of_ri,
            #3rd part
            highest_rd_route,
            lowest_rd_route,
            highest_rd_corridor,
            lowest_rd_corridor,
            highest_rd,
            lowest_rd,
            hpercentage_of_rd,
            lpercentage_of_rd,
            #4th part
            highest_bi_bus,
            lowest_bi_bus,
            highest_bi_route,
            lowest_bi_route,
            highest_bi_corridor,
            lowest_bi_corridor,
            "Rs. "+str(highest_bi),
            "Rs. "+str(lowest_bi),
            hpercentage_of_bi,
            lpercentage_of_bi,
            #Plot
            fig
            )

if __name__ == "__main__":
    app.run_server(debug=False, port = 8080)
