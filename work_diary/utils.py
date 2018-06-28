import requests


if __name__ == '__main__':
    date = {
        'year': '2018',
        'month': '06',
        'day': '28',
        'hour': '15',
        'minute': '32',
    }
    
    filename = '{minute}-{hour}-{day}-{month}-{year}.png'.format(**date)
    resp = requests.post(
        url='http://127.0.0.1:8000/work_diary/api/upload_screenshots/',
        data={
            'description': 'Testing',
            'create_date': '{year}-{month}-{day}T{hour}:{minute}'.format(**date)
        },
        files={
            'image': (filename, open('temp/111.png', 'rb'))
        }
    )
    print(resp.json())
