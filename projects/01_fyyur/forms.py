from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL, ValidationError, Optional

class ShowForm(FlaskForm):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(FlaskForm):
    # Inline validator for Phone, does not need to be called explicitly as long as name follows 'validate_fieldname' format.
    def validate_phone(form, field):
        if field.data:
            error = False
            split_number = field.data.split('-')
            # Check general format
            if len(split_number) == 3:
                # Check section format
                if (len(split_number[0]) == 3) and (len(split_number[1]) == 3) and (len(split_number[2]) == 4):
                    # Check that all are numbers
                    if split_number[0].isdecimal() and split_number[1].isdecimal() and split_number[2].isdecimal():
                        pass
                    else:
                        error = True
                else:
                    error = True
            else:
                error = True
            if error:
                raise ValidationError('Phone Number must be of format XXX-XXX-XXXX')
        else:
            pass  # No phone number present.

    def validate_facebook_link(form, field):
        if field.data:
            error = False
            split_fb_link = field.data.split('/')
            if len(split_fb_link) > 3:
                condition1 = split_fb_link[0] == 'https:'
                condition2 = split_fb_link[1] == ''
                condition3 = split_fb_link[2] == 'www.facebook.com'
                condition4 = split_fb_link[3] != ''

                if condition1 and condition2 and condition3 and condition4:
                    pass
                else:
                    error = True
            else:
                error = True

            if error:
                raise ValidationError('Facebook Link must be of format https://www.facebook.com/XXXX')
        else:
            pass  # No facebook link given
    genre_choices = []
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=[
            ('AL', 'AL'),
            ('AK', 'AK'),
            ('AZ', 'AZ'),
            ('AR', 'AR'),
            ('CA', 'CA'),
            ('CO', 'CO'),
            ('CT', 'CT'),
            ('DE', 'DE'),
            ('DC', 'DC'),
            ('FL', 'FL'),
            ('GA', 'GA'),
            ('HI', 'HI'),
            ('ID', 'ID'),
            ('IL', 'IL'),
            ('IN', 'IN'),
            ('IA', 'IA'),
            ('KS', 'KS'),
            ('KY', 'KY'),
            ('LA', 'LA'),
            ('ME', 'ME'),
            ('MT', 'MT'),
            ('NE', 'NE'),
            ('NV', 'NV'),
            ('NH', 'NH'),
            ('NJ', 'NJ'),
            ('NM', 'NM'),
            ('NY', 'NY'),
            ('NC', 'NC'),
            ('ND', 'ND'),
            ('OH', 'OH'),
            ('OK', 'OK'),
            ('OR', 'OR'),
            ('MD', 'MD'),
            ('MA', 'MA'),
            ('MI', 'MI'),
            ('MN', 'MN'),
            ('MS', 'MS'),
            ('MO', 'MO'),
            ('PA', 'PA'),
            ('RI', 'RI'),
            ('SC', 'SC'),
            ('SD', 'SD'),
            ('TN', 'TN'),
            ('TX', 'TX'),
            ('UT', 'UT'),
            ('VT', 'VT'),
            ('VA', 'VA'),
            ('WA', 'WA'),
            ('WV', 'WV'),
            ('WI', 'WI'),
            ('WY', 'WY'),
        ]
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone', validators=[validate_phone]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()], choices=genre_choices
    )
    facebook_link = StringField(
        'facebook_link', validators=[validate_facebook_link, Optional()]
    )
    website_link = StringField(
        'website_link'
    )

    seeking_talent = BooleanField( 'seeking_talent' )

    seeking_description = StringField(
        'seeking_description'
    )



class ArtistForm(FlaskForm):
    # Inline validator for Phone, does not need to be called explicitly as long as name follows 'validate_fieldname' format.
    def validate_phone(form, field):
        if field.data:
            error = False
            split_number = field.data.split('-')
            # Check general format
            if len(split_number) == 3:
                # Check section format
                if (len(split_number[0]) == 3) and (len(split_number[1]) == 3) and (len(split_number[2]) == 4):
                    # Check that all are numbers
                    if split_number[0].isdecimal() and split_number[1].isdecimal() and split_number[2].isdecimal():
                        pass
                    else:
                        error = True
                else:
                    error = True
            else:
                error = True
            if error:
                raise ValidationError('Phone Number must be of format XXX-XXX-XXXX')
        else:
            pass  # No phone number present.

    def validate_facebook_link(form, field):
        if field.data:
            error = False
            split_fb_link = field.data.split('/')
            if len(split_fb_link) > 3:
                condition1 = split_fb_link[0] == 'https:'
                condition2 = split_fb_link[1] == ''
                condition3 = split_fb_link[2] == 'www.facebook.com'
                condition4 = split_fb_link[3] != ''

                if condition1 and condition2 and condition3 and condition4:
                    pass
                else:
                    error = True
            else:
                error = True

            if error:
                raise ValidationError('Facebook Link must be of format https://www.facebook.com/XXXX')
        else:
            pass  # No facebook link given

    genre_choices = []
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=[
            ('AL', 'AL'),
            ('AK', 'AK'),
            ('AZ', 'AZ'),
            ('AR', 'AR'),
            ('CA', 'CA'),
            ('CO', 'CO'),
            ('CT', 'CT'),
            ('DE', 'DE'),
            ('DC', 'DC'),
            ('FL', 'FL'),
            ('GA', 'GA'),
            ('HI', 'HI'),
            ('ID', 'ID'),
            ('IL', 'IL'),
            ('IN', 'IN'),
            ('IA', 'IA'),
            ('KS', 'KS'),
            ('KY', 'KY'),
            ('LA', 'LA'),
            ('ME', 'ME'),
            ('MT', 'MT'),
            ('NE', 'NE'),
            ('NV', 'NV'),
            ('NH', 'NH'),
            ('NJ', 'NJ'),
            ('NM', 'NM'),
            ('NY', 'NY'),
            ('NC', 'NC'),
            ('ND', 'ND'),
            ('OH', 'OH'),
            ('OK', 'OK'),
            ('OR', 'OR'),
            ('MD', 'MD'),
            ('MA', 'MA'),
            ('MI', 'MI'),
            ('MN', 'MN'),
            ('MS', 'MS'),
            ('MO', 'MO'),
            ('PA', 'PA'),
            ('RI', 'RI'),
            ('SC', 'SC'),
            ('SD', 'SD'),
            ('TN', 'TN'),
            ('TX', 'TX'),
            ('UT', 'UT'),
            ('VT', 'VT'),
            ('VA', 'VA'),
            ('WA', 'WA'),
            ('WV', 'WV'),
            ('WI', 'WI'),
            ('WY', 'WY'),
        ]
    )
    phone = StringField(
        'phone', validators=[validate_phone, Optional()]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()], choices=genre_choices
     )
    facebook_link = StringField(
        'facebook_link', validators=[validate_facebook_link, Optional]
     )

    website_link = StringField(
        'website_link'
     )

    seeking_venue = BooleanField( 'seeking_venue' )

    seeking_description = StringField(
            'seeking_description'
     )

