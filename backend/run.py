from app import create_app
import sys

app = create_app()

if __name__ == '__main__':
    print('=' * 50)
    print('  体重记录系统后端')
    print('  地址: http://127.0.0.1:6000')
    print('=' * 50)
    app.run(debug=False, port=6000, host='127.0.0.1', threaded=True)
