#modules

import flet
from flet import *
from datetime import datetime
import sqlite3

# Necesitamos hacer que se guarde en una base de datps
class DataBase:
    def ConnectToDatabase():
        try:
            db = sqlite3.connect('todo.db')
            c = db.cursor()
            c.execute(
                'CREATE TABLE if not exists tasks (id INTEGER PRIMARY KEY, Task VARCHAR(255) NOT NULL , Date VARCHAR(255) NOT NULL)'
                )
            return db
        except Exception as e:
            print(e)
    def ReadDatabase (db):
        c = db.cursor()
        # no olvides asegurarte del nombre de las columnas no sean SELECT * FROM
        c.execute("SELECT Task, Date From tasks")     
        records = c.fetchall()
        return records   
    
    def InsertDatabase (db , values):
        c = db.cursor()
        # los ?? es por motivos de seguridad
        c.execute("INSERT INTO tasks (Task , Date) VALUES (?,?)" , values)
        db.commit()

    def DeleteDatabase(db ,value):
        c =db.cursor()
        # Aqui eliminamos en base al nombre , y no a un indice
        c.execute("DELETE FROM tasks WHERE Task=?" , value)
        db.commit()    

    def UpdateDatabase(db,value):
        c=db.cursor()
        c.execute("UPDATE tasks SET Task = ? WHERE Task = ?", value)
        db.commit()    
    # Fin del los cruds    


# lets create the form classs first so we xcan get some data

class FormContainer(UserControl):
    # En este punto , podemos psarle en una funcion del main() , para maximizar y minimizar del formulario 
    def __init__(self , func) :
        self.func = func
        super().__init__()

    def build(self):
        return Container(
            width=280,
            height=80,
            bgcolor='bluegrey500',
            opacity=0, # change later
            border_radius=40,
            margin=margin.only(left=-20 , right=-20),
            animate=animation.Animation(400,"decelerate"),
            animate_opacity=200,
            padding=padding.only(top=45,bottom=45),
            content=Column(
                horizontal_alignment=CrossAxisAlignment.CENTER,
                controls=[
                    TextField(
                        height=48,
                        width=255,
                        filled=True,
                        text_size = 12,
                        color = "white",
                        border_color="transparent",
                        hint_text="Description...",
                        hint_style=TextStyle(size=11, color="white"),
                    ),
                    IconButton(
                        content=Text("Add Task"),
                        width=180,
                        height=44,
                        on_click = self.func,# se pasa la funciuon aqui
                        style=ButtonStyle(
                            bgcolor={"":'black'},
                            shape={
                                "":RoundedRectangleBorder(radius=8),
                                },
                        )
                    ),
                   
                ]
            )
        )    
    
# necesitamos una clase para generar las tares cuando el usuario las necesite

class CreateTask(UserControl):
    def __init__(self , task:str , date:str ,func1, func2):
        # crear dos argumentos de tal forma que podamos pasar la funcion de eliminar y deitanr cuyando se cree la instancia
        self.task = task
        self.date = date
        self.func1 = func1
        self.func2 = func2
        super().__init__()

    def TaskDeleteEdit(self , name , color , func):
        return IconButton(
            icon=name,
            width=30,
            icon_size=18,
            icon_color=color,
            opacity=0,
            animate_opacity=200,
            on_click=lambda e:func(self.GetContainerInstance())
        )    
     # necesitamos instacncioas para definirse asimismas
     # ya que se deben identificiar cual eliminar y asi
    def GetContainerInstance(self):
        return self
    
    # para isar;p mecesitamos mantenerlo enn nuestro eliminar editar iconos de boytoners

    def ShowIcons(self,e):
        if e.data == 'true':
            # Estos son los indices de cada icono
            (
                e.control.content.controls[1].controls[0].opacity,
                 e.control.content.controls[1].controls[1].opacity,
            ) = (1,1)
            e.control.content.update()
        else: 
            (
                e.control.content.controls[1].controls[0].opacity,
                 e.control.content.controls[1].controls[1].opacity,
            ) = (0,0)
            e.control.content.update()

    def build(self):
        return Container(
            width=280 , 
            height=60 ,
            border=border.all(0.85,"blue54"),
            border_radius=8,
            on_hover=lambda e: self.ShowIcons(e), #change l;ater
            clip_behavior=ClipBehavior.HARD_EDGE,
            padding=10,
            content=Row(
                alignment=MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    Column(
                        spacing=1,
                        alignment=MainAxisAlignment.CENTER,
                        controls=[
                            Text(value=self.task , size = 10),
                            Text(value=self.date , size=9 , color='white54'),
                        ]
                    ),
                    #Iconos de eliminar y editar
                    Row(
                        spacing=0,
                        alignment=MainAxisAlignment.CENTER,
                        controls=[
                            self.TaskDeleteEdit(icons.DELETE_ROUNDED , 'red500' ,  self.func1),
                            self.TaskDeleteEdit(icons.EDIT_ROUNDED , 'white70' , self.func2),

                        ]
                    )
                ]
            )
        )

def main(page: Page):
    page.horizontal_alignment = 'center'
    page.vertical_alignment = 'center'

    def AddTaskToScreen(e):
        dateTime = datetime.now().strftime("%b-%d , %Y  %I:%M")

        # Podemos usar la base db aqui 
        # configuramos la conexcion con la db
        db = DataBase.ConnectToDatabase()
        DataBase.InsertDatabase(db,(form.content.controls[0].value , dateTime))
        # tenemos ambos valores en la base de datos , el tiempo y la tarea del usuario
        #Cerramos la conexion
        db.close()

        if form.content.controls[0].value:
            _main_column_.controls.append(
                # Ahora tomamos dos instancias de crear tarea
                CreateTask(
                    # Tomamos dos argumentos
                    form.content.controls[0].value,
                    dateTime,

                    DeleteFunction,
                    UpdateFunction,
                )
            )
            _main_column_.update()  
            CreateToDoTask(e)
        else:
            db.close()
            pass    


    
        
    

        # hide function
        CreateToDoTask(e)  

    def DeleteFunction(e):

        db = DataBase.ConnectToDatabase()
        DataBase.DeleteDatabase(
            db,( e.controls[0].content.controls[0].controls[0].value,))
        # cuando eliminaemos , recall esta funcion de la lista

        db.close()
        _main_column_.controls.remove(e)# e es su propia instancia
        _main_column_.update()
    def UpdateFunction(e):
        # la actualizacion sera algo mas compleja
        # queremos editar desde el formulario m entonces tenemos que pasarlo al usuario desde el froms hasta el forms para que cambia las funciones el usuario
        form.height , form.opacity = 200 ,1 # muestra el forms
        (
            form.content.controls[0].value,
            # estamos cambiando la funcion y el nombre
            # necestimaos cambiarla para añadir a la tarea
            form.content.controls[1].content.value,
            form.content.controls[1].on_click,
        ) = (
            e.controls[0]
            .content
            .controls[0]
            .controls[0]
            .value,
            "Update",
            lambda _: FinalizeUpdate(e),
        )
        form.update()

        # una vez el usuario lo edite , tenemos que enviar los datos corregidos

    def FinalizeUpdate(e):

        db = DataBase.ConnectToDatabase()
        DataBase.UpdateDatabase(
            db,
            (
                # se debe obtener la informacion que queremos cambiar
                form.content.controls[0].value,
                # Insertamos la informacion que queremos cambiar
                e.controls[0].content.controls[0].controls[0].value 
            )
        )
        e.controls[0].content.controls[0].controls[0].value = form.content.controls[0].value
        e.controls[0].content.update()
        # entonces podemos mostrar la tarea
        CreateToDoTask

    #funcion para maximizar y minimizar el contenedor
    def CreateToDoTask(e):
        #Cuando hacemo un clic aniade a akgi
        if form.height!=200:
            form.height , form.opacity= 200 , 1
            form.update()

        else:
            form.height , form.opacity = 80 ,0
            # desde podemos remover los valores del campo de texto tambien
            form.content.controls[0].value = None
            form.content.controls[1].content.value = 'Add Text'
            form.content.controls[1].on_click = lambda e: AddTaskToScreen(e)
            form.update()

   



    _main_column_ = Column(
        scroll="hidden",
        expand=True,
        alignment=MainAxisAlignment.START,
        controls=[
            Row(
                alignment=MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    # some title stuffs
                    Text("To-Do Items", size=18,weight="bold"),
                    IconButton(
                        icons.ADD_CIRCLE_ROUNDED,
                       icon_size=18,
                        on_click=lambda e: CreateToDoTask(e),
                    ),
                ],
            ),
            Divider(height=8, color="white24"),
        ]
         
    )

    page.add(
        Container(
            width=1500,
            height=800,
            margin=-10,
            bgcolor="bluegrey900",
            alignment=alignment.center,
            content=Row(
                alignment=MainAxisAlignment.CENTER,
                vertical_alignment=CrossAxisAlignment.CENTER,
                controls=[
                    #Main container
                    Container(
                        width=280 ,
                        height=600,
                        bgcolor = "#0f0f0f",
                        border_radius=40,
                        border=border.all(0.5,"white"),
                        padding=padding.only(top=35,left=20,right=20),
                        clip_behavior=ClipBehavior.HARD_EDGE,# Clip to contest to container 
                        content=Column(
                            alignment=MainAxisAlignment.CENTER,
                            expand=True,
                            controls=[
                                #main columns here
                                _main_column_,
                                # form class here
                                FormContainer(lambda e: AddTaskToScreen(e)),


                            ]

                        )

                    )
                ]
               
            )
        )
    )
    page.update()

    # ka firnar dek cibtebedir ubduce us cini se sugye n bisitris ysanir yb ekenebti ubduce cini varuabke ebtibces vyede ser kkanada facil y rapida
    form= page.controls[0].content.controls[0].content.controls[1].controls[0]
    # mostraremos m lo que necesitamos leer de la base de datos
    # Flet mantendra actualizada la base de datos por las funciones

    # abrir la conexion con la base de datos
    db = DataBase.ConnectToDatabase()
    # recordar que le funcion de la base de datos es almacenar
    #si qwueremos motrar los registros desde el mas nuevo al mas viejo debemos cambiar la lectura [::-1]]
    for task in DataBase.ReadDatabase(db)[::-1]:
        _main_column_.controls.append(
            CreateTask(
                task[0], # primer item para retornar
                task[1],
                DeleteFunction,
                UpdateFunction,
            )
        )

if __name__ == '__main__':
    flet.app(target=main)

#flet.app(main)