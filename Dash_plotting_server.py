import sqlite3
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html

conn = sqlite3.connect('data.sqlite')
df = pd.read_sql_query("SELECT * FROM users", conn)

lstx, lsty = ['A+','A-','B+','B-','O+', 'O-', 'AB+', 'AB-'], []
for i in lstx:
    lsty.append(df[df.blood_group == i].email.count())


app = dash.Dash()

app.layout = html.Div(children=[
    
    dcc.Graph(
        id='example',
        figure={
            'data': [
                {'x': lstx , 'y': [8, 7, 2, 7, 3], 'type': 'bar', 'name': 'Donation Statistics'},
            ],
            'layout': {
                'title': 'Donation Statistics'
            ,   'xaxis':{
                    'title':'Blood Groups'
                },
                'yaxis':{
                     'title':'Number of People'
                     }
                }
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
