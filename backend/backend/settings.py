import os
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

#SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-i+k2*1kxrzh%c=*@gvm^ttt&hc@zq0q-8h4nclqc@0hw#l9_1t'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition
VENDOR_APPS = [
    'simpleui',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework', #DRF
    'rest_framework.authtoken',#DRF
    'captcha', #验证码
    'social_django',#第三方登录
    'corsheaders',#跨域
    'django_ckeditor_5',# 富文本编辑器

]
LOCAL_APPS = [
    'user',# user的目录
    'blog',#文章管理
    'learn',# learn的目录
    'home',# home的目录
    #'admin',# 后台的目录
    'problem',# problem的目录
    'utils',# utils的目录
    'competition',# 比赛的目录
    'judger',# 判题服务的目录
    'AI',# AI的目录
]
INSTALLED_APPS =  LOCAL_APPS + VENDOR_APPS


# 添加 Huey 配置
INSTALLED_APPS += ['huey.contrib.djhuey']

HUEY = {
    'huey_class': 'huey.RedisHuey',  # 使用 Redis 作为存储后端
    'name': 'oj-judger',             # 队列名称
    'results': True,                 # 保存结果
    'store_none': False,             # 当结果为 None 时不存储
    'immediate': True,              # 设置为True，任务会立即执行而不使用Redis队列
    'utc': True,                    # 使用本地时间
    'blocking': True,                # 阻塞式入队
    'consumer': {
        'workers': 4,                # 消费者进程数
        'worker_type': 'thread',     # 线程模式，也可以设置为 'process'
        'initial_delay': 0.1,        # 启动延迟
        'backoff': 1.15,             # 任务失败后重试延迟增加系数
        'max_delay': 10.0,           # 最大重试延迟
        'scheduler_interval': 1,     # 调度间隔
        'periodic': True,            # 启用定期任务
        'check_worker_health': True, # 检查工作进程健康状况
        'health_check_interval': 1,  # 健康检查间隔
    },
    'connection': {
        'host': 'localhost',
        'port': '6379',
        'password': None,  # 如果本地Redis没有设置密码
        'db': 0,
    },
}

# 设置CORS白名单
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]

# 添加允许的请求头
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# 允许的方法
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}

# JWT配置
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),  # access token有效期5分钟
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),    # refresh token有效期1天
    'ROTATE_REFRESH_TOKENS': False,                 # 是否在刷新token时返回新的refresh token
    'BLACKLIST_AFTER_ROTATION': True,               # 是否在刷新token后将旧的token加入黑名单
    'UPDATE_LAST_LOGIN': False,                     # 是否在登录时更新最后登录时间

    'ALGORITHM': 'HS256',                           # 加密算法
    'SIGNING_KEY': SECRET_KEY,                      # 签名密钥
    'VERIFYING_KEY': None,                          # 验证密钥
    'AUDIENCE': None,                               # 接收者
    'ISSUER': None,                                 # 签发者

    'AUTH_HEADER_TYPES': ('Bearer',),              # 认证头类型
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',      # 认证头名称
    'USER_ID_FIELD': 'id',                         # 用户ID字段
    'USER_ID_CLAIM': 'user_id',                    # 用户ID声明

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),  # token类
    'TOKEN_TYPE_CLAIM': 'token_type',              # token类型声明
    'JTI_CLAIM': 'jti',                            # JWT ID声明

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',  # 滑动token刷新过期声明
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),    # 滑动token生命周期
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),  # 滑动token刷新生命周期
}

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'oj',
        'USER':'root',
        'PASSWORD':'8c9fb9417e',
        #'HOST':'localhost',
        'HOST':'116.205.124.191',
        'PORT':'3306',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  # 项目根目录下的 static 目录
    os.path.join(BASE_DIR, 'user', 'static'),  # app1 下的 static 目录
    os.path.join(BASE_DIR, 'blog', 'static'),  # app2 下的 static 目录
    os.path.join(BASE_DIR, 'utils', 'static'),  # app3 下的 static 目录
]
STATIC_ROOT = os.path.join(BASE_DIR, 'statics')
STATIC_CAPTCHA = os.path.join(BASE_DIR, 'utils/static/')
# 用户设置
AUTH_USER_MODEL = 'user.User'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Captcha 验证码设置
CAPTCHA_DPI = 700
CAPTCHA_LENGTH = 4  # 验证码长度
CAPTCHA_TIMEOUT = 0.5  # 验证码过期时间（分钟）
CAPTCHA_FONT_SIZE = 30  # 验证码字体大小
CAPTCHA_IMAGE_SIZE = (100,40)  #图片大小
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.random_char_challenge'  # 随机字符验证码
CAPTCHA_FONT_PATH = os.path.join(BASE_DIR, 'static', 'timesbi.ttf')  # 确保路径正确
# 调整噪声函数，减少噪声
CAPTCHA_NOISE_FUNCTIONS = [
    'captcha.helpers.noise_dots',  # 可选：添加点噪声
    'captcha.helpers.noise_lines',  # 删除线噪声
]


# 富文本编辑器配置

# 首先定义颜色面板
# 定义自定义颜色调色板
customColorPalette = [
    {'color': 'hsl(4, 90%, 58%)', 'label': 'Red'},
    {'color': 'hsl(340, 82%, 52%)', 'label': 'Pink'},
    {'color': 'hsl(291, 64%, 42%)', 'label': 'Purple'},
    {'color': 'hsl(262, 52%, 47%)', 'label': 'Deep Purple'},
    {'color': 'hsl(231, 48%, 48%)', 'label': 'Indigo'},
    {'color': 'hsl(207, 90%, 54%)', 'label': 'Blue'},
    {'color': 'hsl(199, 98%, 48%)', 'label': 'Light Blue'},
    {'color': 'hsl(187, 100%, 42%)', 'label': 'Cyan'},
    {'color': 'hsl(174, 100%, 29%)', 'label': 'Teal'},
    {'color': 'hsl(122, 39%, 49%)', 'label': 'Green'},
    {'color': 'hsl(88, 50%, 53%)', 'label': 'Light Green'},
    {'color': 'hsl(66, 70%, 54%)', 'label': 'Lime'},
    {'color': 'hsl(49, 98%, 60%)', 'label': 'Yellow'},
    {'color': 'hsl(45, 100%, 51%)', 'label': 'Amber'},
    {'color': 'hsl(36, 100%, 50%)', 'label': 'Orange'},
    {'color': 'hsl(14, 100%, 57%)', 'label': 'Deep Orange'},
    {'color': 'hsl(15, 75%, 43%)', 'label': 'Brown'},
    {'color': 'hsl(0, 0%, 62%)', 'label': 'Grey'},
    {'color': 'hsl(200, 18%, 46%)', 'label': 'Blue Grey'},
    {'color': 'hsl(200, 18%, 100%)', 'label': 'White'},
    {'color': 'hsl(0, 0%, 0%, 0.55)', 'label': '半透明黑色'},
    {'color': '#0000008C', 'label': '自定义黑色透明'},
]

# 然后再定义 CKEditor 配置
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                   'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', ],
    },
    'extends': {
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3',
            '|',
            'bulletedList', 'numberedList',
            '|',
            'blockQuote',
        ],
        'toolbar': [
            'heading', '|', 
            'fontFamily', 'fontSize', '|',
            'fontColor', 'fontBackgroundColor', '|',  # 添加字体颜色和背景色工具
            'alignment', '|',
            'bold', 'italic', 'strikethrough', 'underline', 'subscript', 'superscript', '|',
            'link', '|',
            'outdent', 'indent', '|',
            'bulletedList', 'numberedList', '|',
            'blockQuote', '|',
            'insertTable', '|',
            'imageUpload', 'mediaEmbed', '|',
            'code', 'codeBlock', '|',
            'sourceEditing',
            '|',
            'undo', 'redo'
        ],
        'image': {
            'toolbar': [
                'imageTextAlternative', '|',
                'imageStyle:alignLeft', 'imageStyle:alignCenter', 'imageStyle:alignRight', '|',
                'imageStyle:full', 'imageStyle:side', '|',
                'linkImage'
            ],
            'styles': [
                'full',
                'side',
                'alignLeft',
                'alignCenter',
                'alignRight',
            ],
            'resizeOptions': [
                {
                    'name': 'resizeImage:original',
                    # 'value': null,
                    'label': 'Original'
                },
                {
                    'name': 'resizeImage:50',
                    'value': '50',
                    'label': '50%'
                },
                {
                    'name': 'resizeImage:75',
                    'value': '75',
                    'label': '75%'
                }
            ],
        },
        'table': {
            'contentToolbar': [
                'tableColumn', 'tableRow', 'mergeTableCells',
                'tableProperties', 'tableCellProperties'
            ],
            'tableProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            },
            'tableCellProperties': {
                'borderColors': customColorPalette,
                'backgroundColors': customColorPalette
            }
        },
        'heading': {
            'options': [
                {'model': 'paragraph', 'title': 'Paragraph', 'class': 'ck-heading_paragraph'},
                {'model': 'heading1', 'view': 'h1', 'title': 'Heading 1,json', 'class': 'ck-heading_heading1'},
                {'model': 'heading2', 'view': 'h2', 'title': 'Heading 2', 'class': 'ck-heading_heading2'},
                {'model': 'heading3', 'view': 'h3', 'title': 'Heading 3', 'class': 'ck-heading_heading3'}
            ]
        },
        'fontSize': {
            'options': [
                8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72
            ],
            'supportAllValues': 'True' # 允许输入自定义大小
        },
        'alignment': {
            'options': ['left', 'center', 'right', 'justify']
        },
        'fontFamily': {
            'options': [
                'default',
                'Arial, Helvetica, sans-serif',
                'Courier New, Courier, monospace',
                'Georgia, serif',
                'Lucida Sans Unicode, Lucida Grande, sans-serif',
                'Tahoma, Geneva, sans-serif',
                'Times New Roman, Times, serif',
                'Trebuchet MS, Helvetica, sans-serif',
                'Verdana, Geneva, sans-serif',
                '宋体, SimSun',
                '微软雅黑, Microsoft YaHei',
                '黑体, SimHei',
                '楷体, KaiTi',
                'sans-serif,sans-serif'
            ],
            'supportAllValues': 'True'  # 改为字符串 'True'
        },
        'fontColor': {
            'colors': customColorPalette,
            'documentColors': 16,  # 允许从文档中选择颜色
            'supportAllValues': True  # 允许输入自定义颜色值
        },
        'fontBackgroundColor': {
            'colors': customColorPalette,
            'documentColors': 16,
            'supportAllValues': True  # 允许输入自定义颜色值
        }
    }
}

# CKEditor 上传配置
CKEDITOR_5_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
CKEDITOR_5_UPLOAD_PATH = "uploads/"  # 上传路径将在 MEDIA_ROOT 下
# CKEDITOR_5_CUSTOM_CSS = "path-to-your-custom.css"  # 可选：自定义 CSS
# CKEDITOR_5_CONFIGS_PROXY = {  # 可选：代理配置
#     'your-proxy-option': 'your-proxy-value'
# }

# Media files (Uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')



# redis的配置
REDIS_HOST = '116.205.124.191'
REDIS_PORT = 6379
REDIS_PASSWORD = 'whl77585211'
REDIS_DB = 0
REDIS_PROBLEM_DB =1
REDIS_SUBMIT_DB = 2
# 配置 Django 缓存使用 Redis
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SERIALIZER": "django_redis.serializers.json.JSONSerializer",  # 使用JSON序列化器
        }
    }
}

# 使用 Redis 作为会话存储
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# 设置 Redis 作为 Celery 的消息代理（如果使用 Celery）
# CELERY_BROKER_URL = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
# CELERY_RESULT_BACKEND = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

# 设置缓存有效期（秒）
CACHE_TTL = 60 * 15  # 15分钟

# 任务队列配置 - 使用简单的Redis队列
JUDGE_TASK_QUEUE = {
    'HOST': REDIS_HOST,
    'PORT': REDIS_PORT,
    'PASSWORD': REDIS_PASSWORD,
    'DB': REDIS_DB,
    'QUEUE_KEY': 'judge_tasks_queue'
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'whlgc0725@163.com'
EMAIL_HOST_PASSWORD = 'RHtqe38dUxS2SL7S'  # 不是邮箱密码，是授权码
EMAIL_USE_SSL = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

