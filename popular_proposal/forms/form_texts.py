# coding=utf-8
from collections import OrderedDict

WHEN_CHOICES = [
    ('', u'¿Cuándo?'),
    ('1_year', u'1 año'),
    ('2_year', u'2 años'),
    ('3_year', u'3 años'),
    ('4_year', u'4 años'),
]

TOPIC_CHOICES = (('', u'Selecciona una categoría'),
                 ('areasverdes', u'Áreas verdes y espacios públicos'),
                 ('asistencia', u'Asistencia y protección social'),
                 ('conectividad', u'Conectividad y obras'),
                 ('cultura', u'Cultura y patrimonio'),
                 ('deporte', u'Deporte y recreación'),
                 ('diversidad', u'Diversidad e inclusión'),
                 ('educacion', u'Educación'),
                 ('empleabilidad', u'Empleabilidad y emprendimiento'),
                 ('medioambiente', u'Medio ambiente y recolección de basura'),
                 ('participacion', u'Participación y sociedad civil'),
                 ('salud', u'Salud'),
                 ('seguridad', u'Seguridad y prevención de catástrofes'),
                 )

TEXTS = OrderedDict({
    'problem': {'label': u'¿Cuál es el problema o necesidad que se busca solucionar?',
                'preview_question': u'¿Cuál es el problema?',
                'help_text': u'',
                'placeholder': u'Describe el problema que afecta a la comuna (o barrio) del que el alcalde debe hacerse cargo',
                'long_text': "paso1.html"},
    'causes': {'label': u'¿Por qué existe el problema?',
               'preview_question': u'¿Cuáles son las causas?',
               'help_text': u'',
               'placeholder': u'Escribe aquí el último "por qué?", para conocer las causas del problema',
               'long_text': "paso2.html"},
    'solution': {'label': u'¿Qué hay que hacer para lograr la situación ideal?',
                 'preview_question': u'¿Cual sería la solución?',
                 'help_text': u'',
                 'placeholder': u'Siguiendo el ejemplo, propongan la(s) medida(s) que el alcalde debe tomar para solucionar la causa del problema y poder alcanzar la situación ideal.',
                 'long_text': "paso3.html"},
    'solution_at_the_end': {'label': u'¿Qué acción dará por cumplida la tarea del alcalde?',
                            'preview_question': u'¿Cuál sería la solución?',
                            'help_text': u'',
                            'placeholder': u'Define la o las acciones que debe realizar el alcalde para que la propuesta se de por cumplida.',
                            'long_text': "paso4a.html"},
    'when': {'label': u'¿Cuándo?',
             'preview_question': u'¿Cuándo debería estar esto listo?',
             'help_text': u'1_year',
             'placeholder': u'',
             'long_text': "paso4b.html"},
    'title': {'label': u'Colócale título',
              'preview_question': u'Título',
              'help_text': u'',
              'placeholder': u'Título de la propuesta',
              'long_text': "paso5a.html"},
    'clasification': {'label': u'Primero elige una categoría',
                      'preview_question': u'Clasificación',
                      'help_text': u'educacion',
                      'placeholder': u'',
                      'long_text': "paso5b.html"},
    'terms_and_conditions': {'label': u'Términos y condiciones',
                             'preview_question': u'',
                             'help_text': u'',
                             'placeholder': u'',
                             'long_text': "terms_and_conditions.html"},
})
