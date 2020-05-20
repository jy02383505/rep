from setuptools import setup

setup(
    name='rep',
    version='1.0.0.0',
    packages=['core', 'receiver', 'util'],
    py_modules=['refresh_resultd', 'receiverd'],
    scripts=['bin/startup.sh','bin/receiver.sh', 'bin/refresh_result.sh'],
    entry_points={
        'console_scripts': [
            'receiverd=receiverd:main',
            'refresh_resultd=refresh_resultd:main'

        ]
    },
    include_package_data=True,
    zip_safe=False,
    install_requires=[

        'simplejson==3.16.0',
        'httplib2==0.18.0',
        'pymongo==3.0.2',
        'redis==2.10.6'
        # 'paramiko==1.15.2',
        #'requests==2.6.0',
        #'python-etcd==0.4.3',
        #'nose==1.3.4',
        #'pyOpenSSL==16.2.0',
        #'pycrypto==2.6.1'

    ]
)
