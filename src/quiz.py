import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QProgressBar,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

HOUSES = ['Gryffindor', 'Hufflepuff', 'Ravenclaw', 'Slytherin']

HOUSE_COLORS = {
    'Gryffindor': ('#c0392b', '⚔️'),
    'Hufflepuff':  ('#c8971a', '🌻'),
    'Ravenclaw':   ('#2471a3', '📚'),
    'Slytherin':   ('#1e8449', '🐍'),
}

# For each feature, which house corresponds to each answer option (A=0 … D=3).
# Order derived from per-house means in the training dataset, ascending.
HOUSE_ORDER = {
    'Arithmancy':                    ['Gryffindor', 'Slytherin',  'Ravenclaw', 'Hufflepuff'],
    'Astronomy':                     ['Slytherin',  'Ravenclaw',  'Gryffindor','Hufflepuff'],
    'Herbology':                     ['Gryffindor', 'Slytherin',  'Hufflepuff','Ravenclaw'],
    'Defense Against the Dark Arts': ['Hufflepuff', 'Gryffindor', 'Ravenclaw', 'Slytherin'],
    'Divination':                    ['Slytherin',  'Gryffindor', 'Ravenclaw', 'Hufflepuff'],
    'Muggle Studies':                ['Gryffindor', 'Hufflepuff', 'Slytherin', 'Ravenclaw'],
    'Ancient Runes':                 ['Hufflepuff', 'Slytherin',  'Gryffindor','Ravenclaw'],
    'History of Magic':              ['Gryffindor', 'Ravenclaw',  'Slytherin', 'Hufflepuff'],
    'Transfiguration':               ['Gryffindor', 'Hufflepuff', 'Ravenclaw', 'Slytherin'],
    'Potions':                       ['Gryffindor', 'Hufflepuff', 'Ravenclaw', 'Slytherin'],
    'Care of Magical Creatures':     ['Gryffindor', 'Slytherin',  'Hufflepuff','Ravenclaw'],
    'Charms':                        ['Gryffindor', 'Slytherin',  'Hufflepuff','Ravenclaw'],
    'Flying':                        ['Slytherin',  'Hufflepuff', 'Ravenclaw', 'Gryffindor'],
}


def predict_house(answers: dict) -> tuple[str, dict]:
    """Vote-based prediction. Each answer casts one vote for the corresponding house."""
    votes = {h: 0 for h in HOUSES}
    for feature, option_idx in answers.items():
        house = HOUSE_ORDER[feature][option_idx]
        votes[house] += 1
    total = sum(votes.values())
    probs = {h: v / total for h, v in votes.items()}
    return max(probs, key=probs.get), probs


# ── UI strings ────────────────────────────────────────────────────────────

UI = {
    'en': {
        'lang_title':  'Choose your language',
        'title':       'Hogwarts Sorting Quiz',
        'subtitle':    'Answer 13 questions about your magical abilities.\nEach answer reveals which house you align with.',
        'begin':       'Begin Sorting',
        'question_of': 'Question {n} / {total}',
        'belongs':     'You belong in...',
        'sort_again':  'Sort Again',
    },
    'es': {
        'lang_title':  'Elige tu idioma',
        'title':       'Cuestionario de Clasificación de Hogwarts',
        'subtitle':    'Responde 13 preguntas sobre tus habilidades mágicas.\nCada respuesta revela con qué casa te identificas más.',
        'begin':       'Comenzar clasificación',
        'question_of': 'Pregunta {n} / {total}',
        'belongs':     'Perteneces a...',
        'sort_again':  'Volver a intentar',
    },
}

# ── Questions ─────────────────────────────────────────────────────────────

QUESTIONS = {
    'en': [
        {
            'feature': 'Arithmancy',
            'text': 'You must calculate the numerical value of a cursed name using Chaldean numerology. How do you approach it?',
            'options': [
                'Numbers have never been my thing — I just guess',
                'I add up basic values but probably make a few mistakes',
                'I apply the correct system carefully and double-check my work',
                "I've memorised every numerological table — I finish in seconds",
            ]
        },
        {
            'feature': 'Astronomy',
            'text': 'During a midnight observation, you spot an unfamiliar constellation. What do you do?',
            'options': [
                "I go back to sleep — I can barely tell a star from a planet",
                'I try to match it to my star chart but probably misidentify it',
                'I cross-reference multiple charts and note the coordinates carefully',
                'I calculate its position relative to known constellations and log everything',
            ]
        },
        {
            'feature': 'Herbology',
            'text': 'A Mandrake starts screaming while you are repotting it. What happens?',
            'options': [
                'I drop it and run — the sound nearly knocks me out',
                'I panic a little but manage to keep my earmuffs on',
                'I stay calm and follow the repotting procedure correctly',
                'I repot it efficiently, already thinking about its uses in class',
            ]
        },
        {
            'feature': 'Defense Against the Dark Arts',
            'text': 'A Boggart appears in class. What does it transform into when it faces you?',
            'options': [
                'Something terrifying — I freeze on the spot',
                'Something scary, but I manage Riddikulus after a few attempts',
                'I face it confidently and the spell works on the first try',
                'I have rehearsed this — I cast before it even finishes transforming',
            ]
        },
        {
            'feature': 'Divination',
            'text': 'Professor Trelawney asks you to read the tea leaves in your cup. What do you see?',
            'options': [
                'Just tea leaves. I make something up',
                'Vague shapes — I give a generic answer that might be right',
                'I identify a few clear symbols and interpret them reasonably',
                'A complex pattern revealing multiple future events — Trelawney looks impressed',
            ]
        },
        {
            'feature': 'Muggle Studies',
            'text': 'You are asked to explain how a telephone works to the class. How do you do?',
            'options': [
                "I've never seen one — I describe it as a metal talisman",
                'I know it communicates but get the technical details wrong',
                'I explain the basic concept clearly and accurately',
                'I cover signal transmission, networks, and historical development',
            ]
        },
        {
            'feature': 'Ancient Runes',
            'text': 'You find a runic inscription on a cursed artefact. What can you make of it?',
            'options': [
                "I can't tell if it's Futhark or just decoration",
                'I recognise a few common runes but cannot piece the meaning together',
                'I translate most of it and identify it as a warning seal',
                'I translate it fully, identify the dialect and estimate the century',
            ]
        },
        {
            'feature': 'History of Magic',
            'text': 'Professor Binns asks about the Giant Wars of 1637. How do you answer?',
            'options': [
                'I was asleep for that lecture — and most of the others',
                'I remember a few names but mix up the dates',
                'I give a solid summary of the key events and figures',
                'I recite the full timeline, causes and aftermath without notes',
            ]
        },
        {
            'feature': 'Transfiguration',
            'text': 'McGonagall asks you to transfigure a teacup into a tortoise. What happens?',
            'options': [
                'The cup sprouts legs but remains mostly a cup',
                'It becomes vaguely tortoise-shaped but still porcelain',
                'A decent tortoise — correct shape but the pattern is slightly off',
                'A perfect tortoise, indistinguishable from the real thing',
            ]
        },
        {
            'feature': 'Potions',
            'text': 'You are brewing Polyjuice Potion. At what stage are you most likely to make a mistake?',
            'options': [
                'The very first step — I add the wrong ingredient immediately',
                'Somewhere in the middle — I lose track of the stirring direction',
                'I follow each step carefully with only minor timing issues',
                "I don't make mistakes — I've memorised the entire recipe",
            ]
        },
        {
            'feature': 'Care of Magical Creatures',
            'text': 'Hagrid introduces a Hippogriff to the class. What do you do?',
            'options': [
                'Stay at the back and hope it does not notice me',
                'Approach nervously, forgetting to bow properly',
                'Bow respectfully and wait calmly for it to respond',
                'Bow, make eye contact confidently, and stroke it on the first try',
            ]
        },
        {
            'feature': 'Charms',
            'text': 'You need to levitate a heavy cauldron with Wingardium Leviosa. What happens?',
            'options': [
                "Nothing — I cannot get the wrist motion right",
                'It wobbles slightly and tips over',
                'It lifts steadily, a bit slow but controlled',
                'It rises immediately and holds perfectly still',
            ]
        },
        {
            'feature': 'Flying',
            'text': 'On your first flying lesson, Madam Hooch tells you to rise gently. What do you do?',
            'options': [
                'The broom shoots up violently and I barely hang on',
                'I rise too fast but manage not to fall off',
                'I rise smoothly at the right pace',
                'I rise with perfect control and start slow turns before she asks',
            ]
        },
    ],

    'es': [
        {
            'feature': 'Arithmancy',
            'text': 'Debes calcular el valor numérico de un nombre maldito usando numerología caldea. ¿Cómo lo afrontas?',
            'options': [
                'Los números nunca han sido lo mío — simplemente adivino',
                'Sumo los valores básicos pero probablemente cometo errores',
                'Aplico el sistema correcto con cuidado y compruebo mi trabajo',
                'Me sé todas las tablas de memoria — termino en segundos',
            ]
        },
        {
            'feature': 'Astronomy',
            'text': 'Durante una observación de medianoche, distingues una constelación desconocida. ¿Qué haces?',
            'options': [
                'Vuelvo a dormir — apenas distingo una estrella de un planeta',
                'Intento localizarla en mi carta estelar, pero probablemente me equivoco',
                'Comparo varias cartas y anoto las coordenadas con cuidado',
                'Calculo su posición respecto a constelaciones conocidas y lo registro todo',
            ]
        },
        {
            'feature': 'Herbology',
            'text': 'Una Mandrágora empieza a gritar mientras la trasplastas. ¿Qué ocurre?',
            'options': [
                'La suelto y salgo corriendo — el sonido casi me deja inconsciente',
                'Me asusto un poco pero consigo mantener los protectores de oídos',
                'Me mantengo tranquilo y sigo el procedimiento de trasplante correctamente',
                'La trasplanto con eficiencia, ya pensando en sus usos en clase',
            ]
        },
        {
            'feature': 'Defense Against the Dark Arts',
            'text': 'Un Boggart aparece en clase. ¿En qué se transforma cuando te enfrenta?',
            'options': [
                'Algo aterrador — me quedo paralizado en el sitio',
                'Algo que da miedo, pero consigo Riddikulus tras varios intentos',
                'Me enfrento a él con confianza y el hechizo funciona al primer intento',
                'Ya lo había ensayado — lanzo el hechizo antes de que termine de transformarse',
            ]
        },
        {
            'feature': 'Divination',
            'text': 'La profesora Trelawney te pide que leas las hojas de té en tu taza. ¿Qué ves?',
            'options': [
                'Solo hojas de té. Me invento algo',
                'Formas vagas — doy una respuesta genérica que podría ser correcta',
                'Identifico algunos símbolos claros y los interpreto de forma razonable',
                'Un patrón complejo que revela varios eventos futuros — Trelawney queda impresionada',
            ]
        },
        {
            'feature': 'Muggle Studies',
            'text': 'Te piden que expliques a la clase cómo funciona un teléfono. ¿Cómo te sale?',
            'options': [
                'Nunca he visto uno — lo describo como un talismán metálico',
                'Sé que sirve para comunicarse pero me equivoco en los detalles técnicos',
                'Explico el concepto básico con claridad y precisión',
                'Explico la transmisión de señales, las redes y el desarrollo histórico',
            ]
        },
        {
            'feature': 'Ancient Runes',
            'text': 'Encuentras una inscripción rúnica en un artefacto maldito. ¿Qué puedes descifrar?',
            'options': [
                'No sé si es Futhark o simplemente decoración',
                'Reconozco algunas runas comunes pero no consigo darle sentido',
                'Traduzco la mayor parte e identifico que es un sello de advertencia',
                'Lo traduzco completamente, identifico el dialecto y estimo el siglo',
            ]
        },
        {
            'feature': 'History of Magic',
            'text': 'El profesor Binns pregunta sobre las Guerras de los Gigantes de 1637. ¿Cómo respondes?',
            'options': [
                'Me dormí en esa clase — y en casi todas las demás',
                'Recuerdo algunos nombres pero confundo las fechas',
                'Hago un buen resumen de los eventos y personajes clave',
                'Recito la cronología completa, causas y consecuencias sin consultar notas',
            ]
        },
        {
            'feature': 'Transfiguration',
            'text': 'McGonagall te pide que transfigures una taza de té en una tortuga. ¿Qué pasa?',
            'options': [
                'A la taza le salen patas pero sigue siendo en su mayor parte una taza',
                'Adquiere una forma vagamente similar a una tortuga, pero sigue siendo de porcelana',
                'Una tortuga aceptable — forma correcta, pero el patrón es ligeramente imperfecto',
                'Una tortuga perfecta, indistinguible de la real',
            ]
        },
        {
            'feature': 'Potions',
            'text': 'Estás elaborando la Poción Multijugos. ¿En qué etapa es más probable que cometas un error?',
            'options': [
                'En el primer paso — añado el ingrediente equivocado de inmediato',
                'En algún punto intermedio — pierdo la cuenta de la dirección del revuelto',
                'Sigo cada paso con cuidado, con solo pequeños problemas de tiempo',
                'No cometo errores — tengo toda la receta memorizada',
            ]
        },
        {
            'feature': 'Care of Magical Creatures',
            'text': 'Hagrid presenta un Hipogrifo a la clase. ¿Qué haces?',
            'options': [
                'Me quedo al fondo esperando que no me vea',
                'Me acerco nervioso, olvidando hacer la reverencia correctamente',
                'Hago una reverencia respetuosa y espero tranquilo a que responda',
                'Hago la reverencia, mantengo el contacto visual con confianza y lo acaricio al primer intento',
            ]
        },
        {
            'feature': 'Charms',
            'text': 'Necesitas levitar un caldero pesado con Wingardium Leviosa. ¿Qué ocurre?',
            'options': [
                'Nada — no consigo el movimiento de muñeca correcto',
                'Se tambalea un poco y se vuelca',
                'Sube de forma estable, algo lento pero controlado',
                'Sube de inmediato y se queda perfectamente quieto',
            ]
        },
        {
            'feature': 'Flying',
            'text': 'En tu primera clase de vuelo, Madame Hooch te dice que subas con suavidad. ¿Qué haces?',
            'options': [
                'La escoba sube violentamente y apenas me aferro a ella',
                'Subo demasiado rápido pero consigo no caerme',
                'Subo suavemente al ritmo correcto',
                'Subo con un control perfecto y empiezo a hacer giros lentos antes de que me lo pida',
            ]
        },
    ],
}


# ── Styles ────────────────────────────────────────────────────────────────

BG       = '#0d0d1a'
BG_CARD  = '#16213e'
ACCENT   = '#e8b84b'
TEXT     = '#f0e6d3'
DIM      = '#8888aa'

BASE_STYLE = f"""
    QMainWindow, QWidget {{ background-color: {BG}; color: {TEXT}; }}
    QLabel {{ color: {TEXT}; background: transparent; }}
    QProgressBar {{
        border: 1px solid #333355; border-radius: 4px;
        background: #111128; height: 8px;
    }}
    QProgressBar::chunk {{ background: {ACCENT}; border-radius: 4px; }}
"""

OPTION_STYLE = f"""
    QPushButton {{
        background-color: {BG_CARD}; color: {TEXT};
        border: 1px solid #2a2a4a; border-radius: 8px;
        padding: 14px 20px; text-align: left; font-size: 13px;
    }}
    QPushButton:hover {{
        background-color: #2a2a4a; border: 1px solid {ACCENT}; color: {ACCENT};
    }}
"""

LANG_BTN_STYLE = f"""
    QPushButton {{
        background-color: {BG_CARD}; color: {TEXT};
        border: 2px solid #2a2a4a; border-radius: 12px;
        font-size: 18px; font-weight: bold; padding: 20px 40px;
    }}
    QPushButton:hover {{
        background-color: #1e1e3a; border: 2px solid {ACCENT}; color: {ACCENT};
    }}
"""


# ── Screens ───────────────────────────────────────────────────────────────

class LanguageScreen(QWidget):
    def __init__(self, on_select):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)
        layout.setContentsMargins(80, 60, 80, 60)

        icon = QLabel('⚡')
        icon.setFont(QFont('Arial', 56))
        icon.setAlignment(Qt.AlignCenter)

        title = QLabel('Hogwarts')
        title.setFont(QFont('Georgia', 26, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f'color: {ACCENT};')

        btn_row = QHBoxLayout()
        btn_row.setSpacing(30)

        for lang, label in [('en', '🇬🇧  English'), ('es', '🇪🇸  Español')]:
            btn = QPushButton(label)
            btn.setFont(QFont('Arial', 15, QFont.Bold))
            btn.setFixedSize(210, 72)
            btn.setStyleSheet(LANG_BTN_STYLE)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, l=lang: on_select(l))
            btn_row.addWidget(btn)

        layout.addWidget(icon, alignment=Qt.AlignCenter)
        layout.addWidget(title, alignment=Qt.AlignCenter)
        layout.addLayout(btn_row)


class WelcomeScreen(QWidget):
    def __init__(self, on_start):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(60, 40, 60, 40)

        self.icon = QLabel('⚡')
        self.icon.setFont(QFont('Arial', 64))
        self.icon.setAlignment(Qt.AlignCenter)

        self.title = QLabel()
        self.title.setFont(QFont('Georgia', 26, QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet(f'color: {ACCENT};')
        self.title.setWordWrap(True)

        self.subtitle = QLabel()
        self.subtitle.setFont(QFont('Arial', 13))
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setStyleSheet(f'color: {DIM};')
        self.subtitle.setWordWrap(True)

        self.start_btn = QPushButton()
        self.start_btn.setFont(QFont('Arial', 14, QFont.Bold))
        self.start_btn.setFixedSize(260, 52)
        self.start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT}; color: #1a1a00;
                border: none; border-radius: 26px;
                font-size: 15px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #f5cc6a; }}
        """)
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.clicked.connect(on_start)

        for w in (self.icon, self.title, self.subtitle, self.start_btn):
            layout.addWidget(w, alignment=Qt.AlignCenter)

    def set_lang(self, lang: str):
        t = UI[lang]
        self.title.setText(t['title'])
        self.subtitle.setText(t['subtitle'])
        self.start_btn.setText(t['begin'])


class QuestionScreen(QWidget):
    def __init__(self, on_answer):
        super().__init__()
        self.on_answer = on_answer
        self._lang  = 'en'
        self._total = len(QUESTIONS['en'])

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(50, 30, 50, 30)

        prog_row = QHBoxLayout()
        self.prog_label = QLabel()
        self.prog_label.setStyleSheet(f'color: {DIM}; font-size: 12px;')
        self.progress = QProgressBar()
        self.progress.setRange(0, self._total)
        self.progress.setValue(0)
        self.progress.setFixedHeight(8)
        self.progress.setTextVisible(False)
        prog_row.addWidget(self.prog_label)
        prog_row.addWidget(self.progress)
        layout.addLayout(prog_row)

        self.subject_tag = QLabel()
        self.subject_tag.setFont(QFont('Arial', 10))
        self.subject_tag.setStyleSheet(f"""
            color: {ACCENT}; background: #1e1e3a;
            border: 1px solid #2a2a4a; border-radius: 4px; padding: 3px 10px;
        """)
        self.subject_tag.setFixedHeight(26)
        layout.addWidget(self.subject_tag, alignment=Qt.AlignLeft)
        layout.addSpacing(6)

        self.question_label = QLabel()
        self.question_label.setFont(QFont('Georgia', 16))
        self.question_label.setWordWrap(True)
        self.question_label.setStyleSheet(f'color: {TEXT};')
        layout.addWidget(self.question_label)
        layout.addSpacing(10)

        self.option_buttons = []
        for i in range(4):
            btn = QPushButton()
            btn.setStyleSheet(OPTION_STYLE)
            btn.setFont(QFont('Arial', 13))
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, idx=i: self.on_answer(idx))
            self.option_buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

    def load(self, question: dict, idx: int):
        t = UI[self._lang]
        self.prog_label.setText(
            t['question_of'].format(n=idx + 1, total=self._total)
        )
        self.progress.setValue(idx)
        self.subject_tag.setText(f'  📖  {question["feature"]}  ')
        self.question_label.setText(question['text'])
        labels = ['A', 'B', 'C', 'D']
        for i, btn in enumerate(self.option_buttons):
            btn.setText(f'  {labels[i]}.   {question["options"][i]}')

    def set_lang(self, lang: str):
        self._lang = lang


class ResultScreen(QWidget):
    def __init__(self, on_restart):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(18)
        layout.setContentsMargins(60, 40, 60, 40)

        self.subtitle = QLabel()
        self.subtitle.setFont(QFont('Arial', 14))
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setStyleSheet(f'color: {DIM};')

        self.emoji_label = QLabel()
        self.emoji_label.setFont(QFont('Arial', 72))
        self.emoji_label.setAlignment(Qt.AlignCenter)

        self.house_label = QLabel()
        self.house_label.setFont(QFont('Georgia', 34, QFont.Bold))
        self.house_label.setAlignment(Qt.AlignCenter)

        self.scores_label = QLabel()
        self.scores_label.setFont(QFont('Courier', 11))
        self.scores_label.setAlignment(Qt.AlignCenter)
        self.scores_label.setStyleSheet(f'color: {DIM};')

        self.restart_btn = QPushButton()
        self.restart_btn.setFont(QFont('Arial', 13))
        self.restart_btn.setFixedSize(200, 46)
        self.restart_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; color: {ACCENT};
                border: 1px solid {ACCENT}; border-radius: 23px; font-size: 13px;
            }}
            QPushButton:hover {{ background-color: #1e1e0a; }}
        """)
        self.restart_btn.setCursor(Qt.PointingHandCursor)
        self.restart_btn.clicked.connect(on_restart)

        for w in (self.subtitle, self.emoji_label, self.house_label,
                  self.scores_label, self.restart_btn):
            layout.addWidget(w, alignment=Qt.AlignCenter)

    def set_lang(self, lang: str):
        self.subtitle.setText(UI[lang]['belongs'])
        self.restart_btn.setText(UI[lang]['sort_again'])

    def show_result(self, house: str, probs: dict):
        color, emoji = HOUSE_COLORS[house]
        self.emoji_label.setText(emoji)
        self.house_label.setText(house)
        self.house_label.setStyleSheet(f'color: {color};')
        lines = []
        for h, s in sorted(probs.items(), key=lambda x: -x[1]):
            bar = '█' * int(s * 20)
            lines.append(f'{h:<12}  {bar:<20}  {s * 100:.1f}%')
        self.scores_label.setText('\n'.join(lines))


# ── Main Window ───────────────────────────────────────────────────────────

class SortingHatApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Hogwarts Sorting Hat')
        self.setFixedSize(780, 580)
        self.setStyleSheet(BASE_STYLE)

        self._lang    = 'en'
        self._answers = {}
        self._current = 0

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)

        self.lang_screen = LanguageScreen(self._select_lang)
        self.welcome     = WelcomeScreen(self._start_quiz)
        self.question    = QuestionScreen(self._record_answer)
        self.result      = ResultScreen(self._restart)

        for screen in (self.lang_screen, self.welcome, self.question, self.result):
            root.addWidget(screen)

        self._show(self.lang_screen)

    def _show(self, screen: QWidget):
        for s in (self.lang_screen, self.welcome, self.question, self.result):
            s.setVisible(s is screen)

    def _select_lang(self, lang: str):
        self._lang = lang
        self.welcome.set_lang(lang)
        self.question.set_lang(lang)
        self.result.set_lang(lang)
        self._show(self.welcome)

    def _start_quiz(self):
        self._answers = {}
        self._current = 0
        self.question.load(QUESTIONS[self._lang][0], 0)
        self._show(self.question)

    def _record_answer(self, option_idx: int):
        q = QUESTIONS[self._lang][self._current]
        self._answers[q['feature']] = option_idx
        self._current += 1
        total = len(QUESTIONS[self._lang])
        if self._current < total:
            self.question.load(QUESTIONS[self._lang][self._current], self._current)
        else:
            house, probs = predict_house(self._answers)
            self.result.set_lang(self._lang)
            self.result.show_result(house, probs)
            self._show(self.result)

    def _restart(self):
        self._show(self.lang_screen)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setFont(QFont('Arial', 12))
    window = SortingHatApp()
    window.show()
    sys.exit(app.exec_())
