APP PARA TRANSFERIR PLAYLIST DE SPOTIFY A DEEZER
=================

Esta aplicación puede lanzarse de dos formas: 
(RECOMENDADA)
1. Desde el cuaderno **Recommender.ipynb** que se encuentra en la carpeta Spotify y siguiendo los pasos que aparecen(RECOMENDADA)
(OPTATIVA)
2. Desde esta carpeta con los pasos que se comentan a continuación

La primera opción es la recomendada ya que se pueden realizar allí las recomendaciones previamente y asi usar todas las funcionalidades del proyecto.

## Pasos si se elige la segunda opción

Se requiere tener instalado  node.js

1. Registra una aplicación Spotify (usando este enlace como guía https://developer.spotify.com/web-api/tutorial/).
2. Añade la URL http://localhost:8080/spotifyCallback en el apartado de Redirect URIs.
3. Modifique los valores del fichero "api-secrets.js" con los datos del ID de cliente y la key de la aplicacion creada.
4. Registra una aplicación Deezer (usando este enlace como guía http://developers.deezer.com/guidelines/getting_started).
5. Ingresa la URL http://localhost:8080 en el apartado de Application domain, http://localhost:8080/deezerCallback en Redirect URL after authentication y un link aleatorio en Link to your Terms of Use.
6. Modifique los valores del fichero "api-secrets.js" con los datos del ID de aplicacion y la key de la aplicacion creada.

Despues de seguir estos pasos:

En el directiorio base de la aplicación ejecuta el siguiente comando para instalar las dependencias necesarias
   
    $ npm install

Para lanzar la aplicación, ejecuta lo siguiente en el directorio "src"
    
    $ node app.js
