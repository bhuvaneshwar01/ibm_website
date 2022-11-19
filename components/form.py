from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,IntegerField
from wtforms.validators import Length,EqualTo,Email,DataRequired,ValidationError

class Item(FlaskForm):
    Item_name = StringField(label='Item name',validators=[DataRequired()])
    Description = StringField(label='Description',validators=[DataRequired()])
    Available = IntegerField(label='Available (Current stock)',validators=[DataRequired()])
    TotalStock = IntegerField(label='Total stock',validators=[DataRequired()])
    CostPerItem = IntegerField(label='Cost per Item',validators=[DataRequired()])
    submit = SubmitField(label='Submit')

# class Logs(FlaskForm):
#     Quantity = IntegerField(label='Quantity')
