from jinja2 import Template
f

# Crear un diccionario con datos de ejemplo
datos = {
    'usuario1': {'latitud': 1.23, 'longitud': 4.56, 'fecha': '01/01/2022', 'hora': '10:00', 'url': 'foto1.jpg'},
    'usuario2': {'latitud': 7.89, 'longitud': 0.12, 'fecha': '02/01/2022', 'hora': '14:30', 'url': 'foto2.jpg'},
    'usuario3': {'latitud': 3.45, 'longitud': 6.78, 'fecha': '03/01/2022', 'hora': '08:45', 'url': 'foto3.jpg'},
}

# Crear una plantilla HTML
template = Template('''
<table>
  <thead>
    <tr>
      <th>Usuario</th>
      <th>Latitud</th>
      <th>Longitud</th>
      <th>Fecha</th>
      <th>Hora</th>
      <th>URL</th>
    </tr>
  </thead>
  <tbody>
    {% for usuario, datos in diccionario.items() %}
    <tr>
      <td>{{ usuario }}</td>
      <td>{{ datos['latitud'] }}</td>
      <td>{{ datos['longitud'] }}</td>
      <td>{{ datos['fecha'] }}</td>
      <td>{{ datos['hora']
