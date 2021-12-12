# Template project for ssdd-lab

This repository is a Python project template. It contains the
following files and directories:

- `packagename` is the main Python package. You should rename it to
  something meaninful for your project.
- `packagename/__init__.py` is an empty file needed by Python to
  recognise the `packagename` directory as a Python package/module.
- `packagename/cli.py` contains several functions that can handle the
  basic console entry points defined in `python.cfg`. The name of the
  submodule and the functions can be modified if you need.
- `pyproject.toml` defines the build system used in the project.
- `run_client` should be a script that can be run directly from the
  repository root directory. It should be able to run the IceFlix
  client.
- `run_iceflix` should be a script that can be run directly from the
  repository root directory. It should be able to run all the services
  in background in order to test the whole system.
- `setup.cfg` is a Python distribution configuration file for
  Setuptools. It needs to be modified in order to adeccuate to the
  package name and console handler functions.

**@Authors: José Antonio Oliver González-Ortega, Álvaro Pardo Benito, Antonio Patón Rico, Laura Toledo Gutiérrez.**
 # URL repo
https://github.com/SSDD-2021-2022/SSDD_LAB_TEAM_JAAL

 # Funcionamiento del sistema
 Para poner el sistema en funcionamiento, hay que seguir los siguientes pasos(situados en el directorio principal):
 * **1. Ejecutar "run_iceflix"**: ejecutar una instancia de todos y cada uno de los microservicios que forman el sistema
 * **2. Ejecutar "run_client"**: lanza el programa cliente para usar los servicios del sistema
 
 Una vez lanzado el cliente, se mostrará un menú interactivo al usuario para poder ejecutar las diferentes funciones implementadas en el sistema. El primer menú está compuesto de las siguientes opciones:
 * **"1. Conectar"**: opción necesaria para realizar cualquier operación. Si funciona correctamente, informará al usuario de que se ha conectado al sistema.
 * **"2. Autenticar"**: opción previa para acceder a los servicios del sistema distribuido. Debe poner los siguientes datos si quiere acceder al sistema de forma correcta:
    - *usuario*: blas
    - *contraseña*: blas
    
    Una vez autenticado (de forma correcta o no), se mostrará un nuevo menú compuesto de las siguientes opciones:
       
    * **"1. Obtener título por tags"**: se pedirán unos tags al usuario (separados por ',') que servirán como referencia para buscar películas en la base de datos. Las películas que se muestran pueden ser de una búsqueda estricta por tags o simplemente que los contenga.
    * **"2. Añadir tags a un determinado medio"**: se añadirán los tags pedidos al usuario a una determinada película.
    * **"3. Borrar tags"**: se eliminarán los tags demandados por el usuario a una determinada película.
    * **"4. Volver al menú"**: vuelve al menú principal.
    
 * **"3. Opciones de administración"**: contiene funciones dedicadas al administrador del sistema. Para entrar en este área es necesario especificar el token de administración "iceflixadmin". Una vez dentro, se mostrará el siguiente menú:
    
    * **"1. Añadir usuario"**: añade un usuario al sistema.  
    * **"2. Eliminar usuario"**: elimina un usuario del sistema.
    * **"3. Catalogo: Renombrar título"**: renombra un título de una película.

 * **"4. Opciones de catálogo sin autenticación"**: recoge las funciones que se pueden realizar sin necesidad de estar autenticado. Estas son:
    * **"1. Búsqueda por id"**: realiza una búsqueda en la base de datos a través del identificador especificado por el usuario.
    * **"2. Búsqueda por nombre"**: realiza una búsqueda en la base de datos a través del nombre especificado por el usuario.

# Aclaraciones
Respecto a la interacción del usuario con el sistema, hemos dejado acceso a toda la funcionalidad del mismo aún sin autenticación correcta para que salten las excepciones correspondientes, es decir, un usuario puede autenticarse con credenciales incorrectas y aún así "poder realizar" cualquier función sobre el sistema sin ningún impacto en el mismo.

Para ver los datos de entrada al sistema, se deben mirar los archivos ".json" los cuales contienen información acerca de los usuarios, películas, etc.
