
# Servicio de detección en la nube
* Alexis Rodríguez Casañas
* Alberto Martín Núñez

*6 de junio de 2020*

# Índice
1. Objetivo del proyecto y estado del arte.
2. Esquema y arquitectura del proyecto.
3. Funcionamiento.
4. Conclusiones y líneas futuras.

## 1. Objetivo y estado del arte

### Estado

A día de hoy existen muchas empresas que nos ofertan múltiples soluciones cuando nos referimos a seguridad mediante cámaras de vigilancia. La seguridad es un aspecto que esta de modo y uno de los más preocupante para los ciudadanos.

### Problema

Pero, ¿Qué ocurre con la empresa que oferta este servicio?

El computo de este servicio es bastante alto por lo que requiere, a parte del sistema de vigilancia, un computador con la suficiente capacidad de computar la deteccion de imagen en streaming. Un problema de esto supone aumentar el costo del servicio por falta de elementos que lo hagan posible. Lo que requería de una cámara web sencilla y barata se convierte en inviable debido al sistema adjunto que hay que adquirir para realizar la detección.

### Solución

Nosotros proponemos una una solución que está de moda, llevarnos el servicio a la nube. De esta forma el computo no se haría en local sino que nuestra cámara de vigilancia se encargaría de recoger las imágenes en tiempo real y enviárselas a nuestro servicio que estará alojado en la nube. Esto trae consigo muchas ventajas para los clientes como:

- La disminución de costes : Al no necesitar hacer el computo en local los clientes no tienen que pagar mucho dinero por el hardware sino por el servicio que ofrecemos que es mucho más económico.

- Almacenamiento ilimitado: Los clientes no tienen que preocuparse por el espacio. Tenemos que danos cuenta que un servicio como este proporciona bancos y bancos de información y tener una estructura como la que presentamos resulta ser bastante inteligente de cara al servicio que ofertamos.

- Igualdad para los clientes: De esta forma conseguimos que los clientes, sin poseer los recursos hardware y económicos suficientes tengan las mismas ventajas para acceder a nuestro servicio de detección.

  

Uno de los aspecto más importantes que debemos tener en cuenta es la seguridad de los datos. Al ser un servicio detección de intruso la Ley de Protección de Datos puede influir mucho si se toman decisiones inoportunas. Tenemos que tener en cuenta que manejaremos información de muchas cámaras y que esta puede ser sensible para algunos usuarios. La seguridad de los datos que almacenamos tiene que ser una prioridad.

  

También necesitamos ofrecer una alta disponibilidad del servicio, no podemos olvidarnos de que hablamos de la seguridad de los usuarios y un error del sistema puede provocar graves problemas.
## 2. Esquema y arquitectura del proyecto

El proyecto está dividido en varios módulos y servicios que utilizan distintas librerías y herramientas:
### Cliente
El cliente está desarrollado con las tecnologías típicas de front-end (HMTL, JS y CSS). Se compone de la página web y el módulo de streaming para el navegador, el cual está realizado mediante la API `getUserMedia()` del framework **WebRTC**. A diferencia de la web que funciona por protocolo HTTP, la comunicación de vídeo, al tratarse de un envío de imágenes constante funciona a través de **WebSockets**.
### Servidor web
El servidor web es el primer punto de contacto y se encarga de servir la página web y realizar varias funciones. Reenvía el vídeo al servicio de detección de TensorFlow y recibe de vuelta la información del mismo con las detecciones (las coordenadas, tamaño y etiquetas de las boxes a pintar en el navegador), las cuales reenvía al cliente. Cuando el servicio de detección detecta una persona, recibe la imagen con la información de la misma, la cual almacena en un directorio y sube a la base de datos la información de la detección y el nombre de la imagen.

### Servidor de detección
El servidor de detección es un detector típico de TensorFlow convertido en un servicio. En lugar de abrir la cámara web y mostrar en una ventana el vídeo y las detecciones, el programa ha sido modificado para que reciba una imagen y devuelva un JSON con la información necesaria para pintar más adelante estas detecciones (tamaño y posición de las boxes con sus etiquetas).
Al usar la API de TensorFlow, este servicio ya utiliza implícitamente la *GPU* sin necesidad de desarrollo por parte del programador.

![](https://i.ibb.co/wB01MSj/image.png)

### Base de datos
La base de datos es un *MongoDB* en la nube (*Atlas*) y almacena la información de los usuarios y de las detecciones. No almacena las imágenes de la detección, lo cual sería muy ineficiente, sino la información para encontrar las mismas en el servidor.

## Funcionamiento del sistema

El cliente accede al sistema con su cuenta de usuario.

![](https://i.ibb.co/qDkwQ6k/image.png)


Página de bienvenida. Este panel podría incorporar un resumen de las últimas detecciones, créditos gastados en cómputo, etc...

![](https://i.ibb.co/L6MT2SN/image.png)


Para iniciar la vigilancia, se debe acceder al apartado *Detector.* El cliente iniciará ahora el servicio de streaming y comenzará la detección. Nótese que esta detección no está ocurriendo localmente, por lo que cualquier sistema por bajo de recursos que sea (como por ejemplo, una Raspberry) puede ejecutar la funcionalidad.

![](https://i.ibb.co/SrYn482/image.png)


Cuando una persona es detectada, puede ser consultada en el apartado de *Capturas*, donde pueden verse todas las detecciones y la hora de las mismas en una galería.

![](https://i.ibb.co/1qFgcXy/image.png)


## 4. Conclusiones y líneas futuras
Debido al corto periodo de tiempo en el que se realizó el proyecto hay funcionalidades o aspectos de la arquitectura que no han podido ser implementadas o mejoradas. 
El servicio de detección de TensorFlow requiere un gran poder de cómputo y por tanto será cargado a la cuenta del cliente. Por ello, no se puede estar utilizando constantemente y lo más adecuado sería implementar un servicio de detección de movimiento muy simple, el cual es posible implementar sin ningún hardware especial, y que sea este servicio quien despierte unos breves segundos al detector de TensorFlow para que posteriormente volviese a quedar dormido.

Respecto al almacenamiento de imágenes, lo correcto sería utilizar un servidor FTP como se adjunta en el esquema.

Por último, lo más adecuado sería crear imágenes y contenedores de los servicios para poder beneficiarnos de todas las ventajas de los mismos (balanceo de carga bajo demanda, escalabilidad, despliegue automático, etc) y crear una verdadera aplicación cloud-native.

![](https://i.ibb.co/r6gvCs8/image.png)


Como conclusión, en nuestra opinión el proyecto que hemos realizado nos parece sumamente interesante e importante de cara a los clientes que ofertan el servicio de videovigilancia. Como veníamos diciendo en la introducción , la seguridad es un aspecto que está a la orden del día y muchas empresas buscan maximizar sus beneficios disminuyendo el coste que supone comprar y mantener los dispositivos. Esto resulta ser bastante alto debido a la gran cantidad de datos a almacenar y el cómputo que se realiza sobre ellos.

Nos ha resultado realmente interesante el hecho de que un dispositivo con muy bajos recursos pueda ejecutar algo que requiere un gran poder de cómputo con la sensación de que está ocurriendo en tiempo real debido a que este cómputo se está realizando en un clúster remoto.

Por último, nos hemos enfrentado a no pocas dificultades realizando el proyecto debido a que la transmisión de imágenes (más cuando se tratan las mismas con diferentes librerías y se utilizan distintos protocolos) hemos descubierto que no es un problema trivial, al menos para quien no lo había realizado antes. Pero en general, estamos satisfechos con el proyecto.
