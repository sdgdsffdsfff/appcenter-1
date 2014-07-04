#encoding=UTF8
#code by LP
#2013-9-14

import os

class FormFieldBase(object):

    def __init__(self, name, label, data):
        
        self._name = name
        self._label = label
        self._value = ''
        self._error = ''
        self._option = []
        self._attributes = ''

        if data is not None:
            if 'value'  in data:
                self._value = data['value']
            if 'error' in data:
                self._error = data['error']
            if 'option'  in data:
                self._option = data['option']
            if 'attributes'  in data:
                for key in data['attributes'].keys():
                    self._attributes = '%s %s="%s"' % (self._attributes, key, data['attributes'][key])

    def get_name(self):
        return self._name

    def get_label(self):
        return self._label
    
    def get_value(self):
        return self._value

    def error(self):
        return self._error
    
    def is_error(self):
        return self._error != ''

class FormText(FormFieldBase):


    def label(self):
        return '<label for="%s">%s</label>' % (self._name, self._label)

    def field(self):
        return '<input type="text" name="%s" value="%s" %s />' % (self._name, self._value, self._attributes)

class FormHidden(FormFieldBase):

    def label(self):
        return ''

    def field(self):
        return '<input type="hidden" name="%s" value="%s" %s />' % (self._name, self._value, self._attributes)

class FormTextarea(FormFieldBase):

    def label(self):
        return '<label for="%s">%s</label>' % (self._name, self._label)

    def field(self):
        return '<textarea name="%s" %s>%s</textarea>' % (self._name, self._attributes, self._value)

class FormPassword(FormFieldBase):

    def label(self):
        return '<label for="%s">%s</label>' % (self._name, self._label)

    def field(self):
        return '<input type="password" name="%s" value="%s" %s />' % (self._name, self._value, self._attributes)


class FormCheckbox(FormFieldBase):

    def label(self):
        return '<label for="%s">%s</label>' % (self._name, self._label)

                                                        
    def field(self):
        html = ''
        for n,v in self._option:
            checked = ''
            if v in self._value:
                checked = 'checked="checked"'
            html += '<label class="checkbox inline"><input type="checkbox" name="%s" value="%s" %s %s/> %s</label>' % (self._name, v, checked, self._attributes, n)

        return html

class FormRadio(FormFieldBase):

    def label(self):
        return '<label for="%s">%s</label>' % (self._name, self._label)

    def field(self):
        html = ''
        for n,v in self._option:
            checked = ''
            try:
                if float(v) == float(self._value):
                    checked = 'checked="checked"'
            except ValueError:
                pass
            html += '<label class="radio inline"><input type="radio" name="%s" value="%s" %s %s/> %s</label>' % (self._name, v, checked, self._attributes, n)
        return html

class FormSelect(FormFieldBase):

    def label(self):
        return '<label for="%s">%s</label>' % (self._name, self._label)

    def field(self):
        html = '<select name="%s" %s>\n' % (self._name, self._attributes)
        for n,v in self._option:
            checked = ''
            if v == self._value:
                checked = 'selected="selected"'
            html += '<option value="%s" %s>%s</option>\n' % (v, checked, n)
        html += '</select>\n'
        return html

class FormFile(FormFieldBase):
    
    def label(self):
        return '<label for="%s">%s</label>' % (self._name, self._label)

    def field(self):
        return '<input type="file" name="%s" %s />' % (self._name, self._attributes)

class FormSubmit(FormFieldBase):
    
    def __init__(self, name, value, data):      
        self._name = name
        self._value = value
        if data is not None:
            if 'class' in data:
                self._attributes = 'class="%s"' % data['class']

    def field(self):
        return '<input type="submit" name="%s" value="%s" %s />' % (self._name, self._value, self._attributes)

def FormElementField(form, name):

    for x in form.field_list():
        if x.get_name() == name:
            return x

    raise FormException("no field found")

def FormElementSubmit(form, name):

    for x in form.button_list():
        if x.get_name() == name:
            return x

    raise FormException("no button found")

def Field(field_type, name, label, data):
    return eval('Form' + str(field_type).capitalize())(name, label, data)

def Button(field_type, name, value, data):
    return eval('Form' + str(field_type).capitalize())(name, value, data)

class Form(object):

    def __init__(self, name, request, session):

        self._request = request
        self._session = session
        self._name = name
        self._fields = {}
        self._buttons = {}
        self._enctype = 'enctype="application/x-www-form-urlencoded"'
        self._validators = []
        self._index = 0
        self._errors = []

        if self._request.method == 'POST':
            if '__TOKEN__' not in self._request.form or '__TOKEN__' not in self._session:
                raise FormException("token not exists")
            if self._session['__TOKEN__'] != self._request.form['__TOKEN__']:
                raise FormException("token error")
        
        form_token = ''.join(map(lambda xx:(hex(ord(xx))[2:]),os.urandom(16)))
        self._session['__TOKEN__'] = form_token
        self._token = form_token

    def add_field(self, field_type, label, name, data=None):
        self._fields[name] = {'type': field_type, 'label': label, 'data': data, 'index': self._index}
        if field_type == 'file':
            self._enctype = 'enctype="multipart/form-data"'
        self._index += 1
    
    def add_submit(self, name, value, data=None):
        self._buttons[name] = {'value': value, 'data':data}

    def begin_form(self):
        return '<form name="%s" method="post" %s>\n\t<input type="hidden" name="__TOKEN__" value="%s" />' % (self._name, self._enctype, self._token)

    def end_form(self):
        html = ''
        for hidden in self.hidden_field_list():
            html = '%s\n%s' % (html, hidden.field())
        return '\n%s\n</form>' % html
    
    def get_fields(self):
        return self._fields

    def field_list(self):

        out_put = []
        for x in xrange(0, self._index):
            for key in self._fields.keys():
                if self._fields[key]['index'] == x and self._fields[key]['type'] != 'hidden':
                    out_put.append(Field(self._fields[key]['type'], key, self._fields[key]['label'], self._fields[key]['data']))

        return out_put

    def hidden_field_list(self):
        out_put = []
        for x in xrange(0, self._index):
            for key in self._fields.keys():
                if self._fields[key]['index'] == x and self._fields[key]['type'] == 'hidden':
                    out_put.append(Field(self._fields[key]['type'], key, self._fields[key]['label'], self._fields[key]['data']))
        return out_put

    def button_list(self):
        
        out_put = []
        for key in self._buttons.keys():
            out_put.append(Button('submit', key, self._buttons[key]['value'], self._buttons[key]['data']))

        return out_put

    def add_error(self, name, error):

        if 'data' not in self._fields[name] or self._fields[name]['data'] is None:
            self._fields[name]['data'] = {}
        self._fields[name]['data']['error'] = error
        self._errors.append((name, error))

    def has_error(self):

        return not len(self._errors) == 0
    
    def get_errors(self):
        return self._errors

    def set_value(self, data=None):
        if data == None:
            data = self._request.form
        for key in data.keys():
            if key in self._fields.keys():
                if 'data' not in self._fields[key] or self._fields[key]['data'] is None:
                    self._fields[key]['data'] = {}

                if self._fields[key]['type'] == 'checkbox':
                    try: 
                        self._fields[key]['data']['value'] = data.getlist(key)
                    except:
                        self._fields[key]['data']['value'] = data[key]
                else:
                    self._fields[key]['data']['value'] = str(data[key])

        for key in self._request.files.keys():
            self._fields[key]['data']['value'] = self._request.files[key]
    
    def clean_value(self):
        #清空
        for key in self._fields.keys():
           self._fields[key]['data']['value'] = ''

    def add_message(self, status, message):
        self._status = status
        self._message = message

    def message(self):
        try:
            return '''
            <div class="alert alert-%s">
                <button class="close" data-dismiss="alert"></button>
                %s
            </div>
            ''' % (self._status, self._message)
        except:
            return ''

    def status(self):
        try:
            return self._status
        except Exception:
            return ''

    def add_validator(self, validator_obj):
        self._validators.append(validator_obj)

    def validate(self):
        self.set_value()
        for validate_obj in self._validators:
            obj = validate_obj()
            obj.validate(self)
        if self.has_error():
            return False
        
        return True

class FormValidatorAbstract(object):

    def validate(self, form_obj):
        self._form = form_obj
        rules = self.rules()
        for field in rules.keys():
            self._parse_rule(field, rules[field])

    def _parse_rule(self, field, rule):
        try:
            value = self._form.get_fields()[field]['data']['value']
        except:
            value = ''

        if 'required' in rule:
            if rule['required'] == True:
                try:
                    if value == None or value == '' or len(value) == 0:
                        self._form.add_error(field, '不能为空')
                except TypeError, ex:
                    if value.filename == '':
                        self._form.add_error(field, '不能为空')
                except:
                    pass

        if 'min_length' in rule:
            min_length = int(rule['min_length'])
            length = len(value)
            if length > 0 and length < min_length:
                self._form.add_error(field, '长度不能小于 %s' % min_length)

        if 'max_length' in rule:
            max_length = int(rule['max_length'])
            length = len(value)
            if length > 0 and length >= max_length:
                self._form.add_error(field, '长度不能大于 %s' % max_length)

        if 'validate' in rule:
            error = rule['validate'](value)
            if error != True:
                self._form.add_error(field, error)

class FormException(Exception):
    pass