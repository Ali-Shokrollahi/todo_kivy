from kivymd.app import MDApp
from kivy.core.window import Window
from kivymd.uix.button import MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.picker import MDThemePicker
from kivymd.uix.list import TwoLineAvatarIconListItem, ILeftBodyTouch
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.utils import platform
from kivymd.uix.snackbar import Snackbar
import arabic_reshaper
from bidi.algorithm import get_display
import jdatetime
from database import Database

db = Database()

Window.size = (360, 600)


class ListItemWithCheckbox(TwoLineAvatarIconListItem):
    '''Custom list item'''
    task = None
    task_dialog = None

    def __init__(self, pk=None, **kwargs):
        super().__init__(**kwargs)
        # state a pk which we shall use link the list items with the database primary keys
        self.pk = pk

    def mark(self, check, the_list_item):
        '''mark the task as complete or incomplete'''
        if check.active == True:
            the_list_item.text = '[s]' + the_list_item.text + '[/s]'
            db.mark_task_as_complete(the_list_item.pk)  # here
        else:
            the_list_item.text = str(db.mark_task_as_incomplete(the_list_item.pk))  # Here

    def open_content(self, task):
        self.task = task
        box = MDBoxLayout(orientation="vertical", size_hint=(1, None), height="200dp")
        card = MDCard(padding=[15, 15, 15, 15])
        card.add_widget(MDLabel(text=task.secondary_text, pos_hint={'center_y': 0.7}))

        btn = MDIconButton(icon='trash-can-outline', pos_hint={"center_x": .5},

                           )
        btn.theme_text_color = "Custom"
        btn.text_color = [1, 0, 0, 1]

        box.add_widget(card)
        box.add_widget(btn)
        btn.bind(on_press=self.delete_item)
        btn.bind(on_release=self.closeD)

        self.task_dialog = MDDialog(
            title=task.text,
            type="custom",
            content_cls=box)
        self.task_dialog.open()

    def delete_item(self, instance):
        '''Delete the task'''
        self.parent.remove_widget(self.task)
        db.delete_task(self.task.pk)  # Here

    def closeD(self, instance):
        self.task_dialog.dismiss()


class LeftCheckbox(ILeftBodyTouch, MDCheckbox):
    '''Custom left container'''


class MainApp(MDApp):
    pri = None

    def build(self):
        self.theme_cls.primary_palette = "Orange"
        self.theme_cls.theme_style = "Dark"

    def on_start(self):
        """Load the saved tasks and add them to the MDList widget when the application starts"""
        try:
            completed_tasks, uncomplete_tasks = db.get_tasks()

            if uncomplete_tasks != []:
                for task in uncomplete_tasks:
                    add_task = ListItemWithCheckbox(pk=task[0], text=task[1], secondary_text=task[2],
                                                    )
                    if task[3] == 'important':
                        add_task.ids.impIcon.icon = 'clock-fast'

                    self.root.ids.container.add_widget(add_task)

            if completed_tasks != []:
                for task in completed_tasks:
                    add_task = ListItemWithCheckbox(pk=task[0], text='[s]' + task[1] + '[/s]', secondary_text=task[2])
                    add_task.ids.check.active = True
                    self.root.ids.container.add_widget(add_task)
        except Exception as e:
            print(e)
            pass

    def changeTheme(self):
        if self.theme_cls.theme_style == "Dark":
            self.theme_cls.theme_style = "Light"

        else:
            self.theme_cls.theme_style = "Dark"

    def show_theme_picker(self):
        theme_dialog = MDThemePicker()
        theme_dialog.open()

    def date(self):
        tday = "تاریخ امروز:"
        tdate = str(jdatetime.date.today())
        tday = arabic_reshaper.reshape(tday)
        tday = get_display(tday)
        return tdate + tday

    def checked(self, value):
        self.pri = value

    def add_task(self, task_title, task_des):
        '''Add task to the list of tasks'''
        if task_title == "" or self.pri is None:
            error = Snackbar(text="please fill out the form.", size_hint_x=0.95,
                             pos_hint={'center_x': 0.5, 'y': 0.01}, duration=1)
            error.open()

        else:
            created_task = db.create_task(task_title.strip(), self.pri, task_des.strip())
            error = Snackbar(text="Added Successfully.", size_hint_x=0.95,
                             pos_hint={'center_x': 0.5, 'y': 0.01}, duration=1)
            error.open()
            list_task = ListItemWithCheckbox(pk=created_task[0],
                                             text='[font=gandom]' + '[b]' + created_task[1] + '[/b]' + '[/font]',
                                             secondary_text=created_task[2],
                                             )
            if self.pri == 'important':
                list_task.ids.impIcon.icon = 'clock-fast'
            self.root.ids['container'].add_widget(list_task
                                                  )  # Here


if __name__ == '__main__':
    MainApp().run()
