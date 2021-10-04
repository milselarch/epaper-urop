from Updater import Updater
from datetime import datetime

import cProfile

def make_date_stamp():
    return datetime.now().strftime("%y%m%d-%H%M")

updater = Updater()

def run():
    try:
        updater.run()
        return

        updater.run([
            'screenshots/shot-0.png', 'screenshots/shot-1.png'
        ])

        """
        updater.chunk_load_image('screenshots/shot-0.png')
        updater.run([
            'screenshots/shot-0.png', 'screenshots/shot-1.png'
        ])
        """
    except KeyboardInterrupt:
        return


if __name__ == '__main__':
    start_time = datetime.now().timestamp()
    profiler = cProfile.Profile()
    result = profiler.runcall(run)
    end_time = datetime.now().timestamp()
    duration = end_time - start_time

    stamp = make_date_stamp()
    filepath = f'profiles/profile-{stamp}'
    profiler.dump_stats(filepath)
    print(f'profile saved to {filepath}')