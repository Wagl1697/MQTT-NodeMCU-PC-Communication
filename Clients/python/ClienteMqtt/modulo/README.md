# clientes_mqtt

# Encriptación TLS
Esta es una serie de pasos a seguir en caso de que se requiera configurar un broker mosquitto con una encriptación.

## ¿Que es TSL?

El protocolo TSL (Transport Layer Segurity) es una capa de protocolo que puede colocar una red a conexion fiable (ej: TCP/IP), proporciona una comunicacion segura entre servidor y cliente, al permitir una autenticacion mutua, el uso de firmas digitales para la integridad y el cifrado para la privacidad. 

Para esto se utiliza una firma digital (certificado) y llaves públicas y privadas; para encriptar y desencriptar el mensaje.

# Pasos a seguir:

- Crear una clave pública y una privada para la autoridad de certificación (CA).
- Crear un certificado para la CA y firmarlo con la clave privada antes generada.
- Generar una clave pública y una privada para el broker MQTT.
- Crear un requerimiento de firma de certificado para las claves del paso anterior.
- Utilizar el certificado del paso 2 para firmar el requerimiento del paso anterior.
- Copiar todos los certificados en un directorio del broker MQTT.
- Copiar el certificado de la CA en el cliente.
- Editar la configuración de Mosquitto.
- Editar la configuración del cliente para que utilice TLS y el certificado de la CA.


**requisito**: instalar ssl —> `sudo apt-get install openssl`

1. Crear el par de claves para la CA
**`sudo openssl genrsa -des3 -out ca.key 2048`
```bash
Enter pass phrase for ca.key: mqtt 
```
2. Crear un certificado para la CA y firmarlo

`sudo openssl req -new -x509 -days 1826 -key ca.key -out ca.crt`
Ejemplo de salida (ya completado con datos)
```bash
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) [AU]:AR
State or Province Name (full name) [Some-State]:Entre-Rios
Locality Name (eg, city) []:Oro-Verde
Organization Name (eg, company) [Internet Widgits Pty Ltd]:Iot-UNER
Organizational Unit Name (eg, section) []:
Common Name (e.g. server FQDN or YOUR name) []:war-machine-uner  
Email Address []:ejemplo@gmail.com
```

3. Crear un par de claves para el broker MQTT
**`sudo openssl genrsa -out server.key 2048`**

```bash
Generating RSA private key, 2048 bit long modulus (2 primes)
.......+++++
............+++++
e is 65537 (0x010001)
```

4. Crear un certificate request
(Es un archivo .csr)
En este paso se pide los mismos datos que la creacion del certificado de autoridad (CA) sin embargo se recomienda no completar todo con los mismos dato (por ej omitiendo city)

`sudo openssl req -new -out server.csr -key server key`

Con esto se crea el certificado del broker

5. Firmar el requerimiento del certificado
    
    **`sudo openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 360`**
    
    ```bash
    $ sudo openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 360
    Signature ok
    subject=C = AR, ST = Entre-Rios, O = Iot-UNER, CN = machine-house, emailAddress = andresvenialgo15@gmail.com
    Getting CA Private Key
    Enter pass phrase for ca.key:
    ```
    
6. Ver los archivos creados:
Deberian ser: los archivos certificados y llaves TLS/SSL
`ca.crt`, `ca.key`, `ca.srl`, `server.crt`, `server.csr`, `server.key` 
El archivo ca.key no se copia en el broker, ni el el cliente ya que es para generar nuevos certificados.

7. Copiar los archivos al broker
Los archivos a copiar serian ca.crt, server.crt y server.key en los directorios de configuraciòn de mosquitto. Estos estan en /etc/mosquitto 

```bash
sudo cp ca.crt /etc/mosquitto/ca_certificates
sudo cp server.crt server.key /etc/mosquitto/certs/
```

8. Copiar los certificados en el cliente
Es pegar el archivo ca-crt en nuestro cliente

9. Configurar mosquitto
Hay que configurar el archivo mosquitto.conf
aclaracion: puede ser mosquitto.conf en ves de mosquitto.conf.example

```bash
sudo cp /usr/share/doc/mosquitto/examples/mosquitto.conf.example /etc/mosquitto/conf.d/mosquitto.conf
```

Luego se edita con 

```bash
sudo nano /etc/mosquitto/conf.d/mosquitto.conf
```

```bash
port 8883 
cafile /etc/mosquitto/ca_certificates/ca.crt
certfile /etc/mosquitto/certs/server.crt
keyfile /etc/mosquitto/certs/server.key
```

Se guarda el archivo y luego ejecutamos el comando `sudo service mosquitto restart`, y para verificar esto se puede ejecutar el comando `sudo systemctl status mosquitto.service` 

10. Prueba de conexion con el broker

```bash
mosquitto_sub -t test -h localhost -p 8883 -s -cafile ca.crt -v
```

```bash
mosquitto_pub -t test -h localhost -p 8883 -s -cafile ca.crt -m "hola mundo" 
```

Notas de algunos parametros
