### Дляподключения авторизации через OAuth2 google используйте следующие данные:

Чтобы включить функцию Google sign up, сначала необходимо создать ключ OAuth Client. Перейдите в 
[Google Cloud Console]( https://console.cloud.google.com/welcome/new), выберите проект, который вы хотите использовать, и выполните поиск «API Credentials»:
![screenshot](https://pythonist.ru/wp-content/uploads/2023/09/google-console-api-credentials-search-1024x819.png)

Далее нажмите на кнопку «Create credentials» и выберите в выпадающем списке «OAuth Client ID»:
![screenshot](https://pythonist.ru/wp-content/uploads/2023/09/google-console-create-credentials-1024x819.png)

Выберите «Web-приложение», задайте пользовательское имя и добавьте URL-адрес вашего фронтенда в качестве URI авторизованного перенаправления. Для удобства тестирования я рекомендую также добавить:

`http://127.0.0.1:3000`

`http://127.0.0.1:3000/api/auth/callback/google`

`https://developers.google.com/oauthplayground`

Наконец, нажмите кнопку «Создать», чтобы сгенерировать учетные данные:
![screenshot](https://pythonist.ru/wp-content/uploads/2023/09/google-console-oauth-create-1024x819.png)

Вам будут представлены «Идентификатор клиента» и «Секрет клиента». 
## Запишите их в файл backend_api/settings:

`SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'Идентификатор клиента'`
`SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'Секрет клиента'`

### Шаблон

В шаблоне вы можете добавить подобный код для получения иконки с url авторизации

`<a href="{% url 'social:begin' 'google-oauth2' %}"><img src="/static/lgoogle.png" class="avatar-3" data-toggle="tooltip" title="{% trans 'Login via Google+' %}"></a>`

url перенаправления  на страницу google для авторизвции
`'https://0.0.0.0:80/auth/login/google-oauth2/'`



### Дляподключения авторизации через OAuth2 vk используйте следующие данные:

### Настройка ключей для авторизации через OAuth2 vk

Чтобы их получить, нужно создать в инструментарии разработчика ВКонтакте приложение и взять ID вашего приложения и секретный ключ для него.

Регистрируем приложение:
![screenshot](https://evileg.com/media/uploads/2018/07/13/screenshot_20180712_230524.png)

Заходим в его настройки и видим всё, что нужно
![screenshot](https://evileg.com/media/uploads/2018/07/13/screenshot_20180712_230609.png)

В итоге прописываем в данные переменные в файле backend_api/settings следующие настройки:

`SOCIAL_AUTH_VK_OAUTH2_KEY = 'ID приложения'`
`SOCIAL_AUTH_VK_OAUTH2_SECRET = 'Секрет приложения'`

url перенаправления  на страницу vk для авторизвции
`'https://0.0.0.0:80/auth/login/vk-oauth2/'`