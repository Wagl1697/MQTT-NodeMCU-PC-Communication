# -*- coding: utf-8 -*-
"""
Created on Sat Aug 27 09:49:53 2022

@author: Andres Venialgo
"""

import paho.mqtt.client as mqtt
import os
import psutil
from time import sleep
import json
from uuid import getnode as get_mac
from datetime import datetime

class Cliente_mqtt():
    def __init__(self, p_host, p_port):
        """
        El atributo intentos_conexion es la cantidada de intentos que se permite 
        intentar conectar con el broker

        Parameters
        ----------
        p_host : str
            
        p_port : int
            DESCRIPTION.

        Returns
        -------
        None.

        """
        # self.will = self.cargar_will()
        self.client = mqtt.Client()
        # self.client.will_set(self.will["topic"], self.will['payload'],qos = 0)
        self.host = p_host
        self.port = p_port
        self.connflag = False
        self.intentos_fallidos = 0
        self.intentos_conexion = 5
    
    def on_connect(self, client, userdata, flags, rc):
        """
        Esta funcion es llamada cuando el broker responde a la solicitud 
        de conexión

        Parameters
        ----------
        client : paho.mqtt.client
            Es el la instancia actual
        userdata : TYPE
            Son los datos del usuario cargados en el constructor
            o por el user_data_set()
        flags : int
            Es una bandera enviada por el broker
        rc : int
            Es el resultado de la conexion
            0: conexion exitosa
            1: conexion rechazada: version del protocolo incorrecta
            2: conexino rechazada: identificador de cliente no valida
            3: conexion rechazada: servidor no disponible
            4: conexion rechazada: nombre de usuario o contraseña incorrecto

        Returns
        -------
        None.

        """
        self.connflag = True
        print ('Se conecto al broker')
    
    def on_disconnect(self, client, userdata, rc):
        """
        Esta funcion es llamada cuando el broker responde a la solicitud 
        de conexión

        Parameters
        ----------
        client : paho.mqtt.client
            Es el la instancia actual
        userdata : TYPE
            Son los datos del usuario cargados en el constructor del cliente.mqtt
            o por en la funcion paho.mqtt.client.user_data_set()
        rc : 
        Es el resultado de la desconexion y pueden ser
        MQTT_ERR_SUCCESS  
        (0) si es el callback por llamar a la funcion disconnect()
        Returns
        -------
        None.
        """
        self.connflag == False
        print ('Se desconecto del broker')
        
    def desconectar_broker(self):
        self.client.disconnect()
        self.client.on_disconnect = self.on_disconnect
        self.client.loop_stop()
        self.connflag = False

    def __del__(self):
        self.client.disconnect()
        self.client.on_disconnect = self.on_disconnect
        
    def on_publish(self,client,userdata, mid):
        """
        Esta funcion se llama cuando la publicacion fue exitosa
        Parameters
        ----------
        client : paho.mqtt.Client
            Es la instancia actual
        userdata : str
            Son los datos cargados en el constructor del objeto c
        mid : str
            Es el mensaje actual que se esta mandando
        Returns
        -------
        None.

        """
        print("publish: ", mid)
        
    def cargar_will(self):
        """
        Esta funcion permite cargar el testamento del cliente
        Returns
        -------
        will : dict
            devuelve el topico y el mensaje a publicar

        """
        topic = str(self.obtener_mac()) +'/will'
        with open('will.txt','r') as archivo:
            mensaje = archivo.readlines()
        testamento = ''
        for it in mensaje:
            testamento += it
        will = {'topic':f'{topic}','payload':f'{testamento}'}
        return will
    
    def obtener_mac (self):
        """

        Returns
        -------
        mac : TYPE
            DESCRIPTION.

        """
        mac = get_mac()
        mac = ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))
        return mac
    
    def conectar_broker(self):
        """
        Esta funcion se encarga de manejar la conexion al broker e inicializar
        los procesos de mqtt en caso de exito. 

        Returns
        -------
        Bool
            Devuelve un booleano en funcion de si se pudo conectar al broker

        """
        try:
            print("Conectando al broker...")
            value = self.client.connect( self.host, self.port)
            self.client.loop_start()
            self.client.on_connect = self.on_connect
            sleep(3)

        except Exception as msg:
            print (f"Ocurrio una excepcion {msg}")
            return False
        else:
            if (value == 0):
                return self.connflag
            else:
                return False
        
            
    def cargar_datos(self):
        """
        En esta funcion se carga los datos a publicar

        Returns
        -------
        datos : list
            Es una lista donde sus elementos son diccionarios
        """
        try:
            
            aux = datetime.fromtimestamp(psutil.boot_time())
            hora_inicio = aux.strftime('%Y-%m-%d %H:%M:%S')
            hora_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ram = psutil.virtual_memory()
            datos = self.leer_topicos()
            
            payload = [str(hora_inicio),str(hora_actual),\
                str(ram[0]),str(ram[2]),str(ram[3])]
        except Exception as msg:
            #TODO lanzo una excepcion? lo muestro?
            pass
            
        else:
            for it in range (len(datos)): 
                #La dimension de datos y de los topicos deben ser iguales
                datos[it]['payload'] = payload[it]    
            return datos
        
    def leer_topicos(self):
        """
        Esta funcion lee los topicos que estan guardados 
        en un archivo json.

        Returns
        -------
        data : dict

        """
        try:
            with open('topicos/topics.json','r') as file:
                data = json.load (file)
        except FileNotFoundError as msg:
            print("Error en leer los topicos")
            
        return data
        
    def run(self):
        """
        Esta funcion el la funcion principal del cliente mqtt, es la que permite
        administrar la conexion con el broker y publicacion de los datos

        Returns
        -------
        None.

        """
        while True:
            try:
                for intentos in range(self.intentos_conexion):
                    if not self.connflag:
                        if self.conectar_broker():
                            break
                        else:
                            self.intentos_fallidos += 1
                    sleep(2)
            except Exception as msg:
                print(f"No se pudo conectar al broker:{msg} ")
            
            else:
                while self.connflag == True:
                    mensaje = self.cargar_datos()
                    for it in mensaje:
                        self.client.publish( it["topic"], it["payload"])
                        sleep(2)

    
        
if __name__ == '__main__':
    pub = Cliente_mqtt('localhost', 1883)
    pub.conectar_broker()
    pub.desconectar_broker()
    dato = pub.cargar_will()
    print(dato)
    #pub.__del__()
    # pub.__del__()
    # pub.run()

                
                
        
        
             