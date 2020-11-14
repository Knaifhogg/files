import concurrent.futures
from multiprocessing import RLock, freeze_support
from tqdm import tqdm
import time

def inner_function(**node):
    """Inner function simulating a long running function"""
    node_kwarg = {
        'desc': "In: " + node['letter'],
        'ascii': True,
        'bar_format': '{desc}: {elapsed_s:.1f}',
        'leave': True
    }
    with tqdm(**node_kwarg) as inner_progress:
        time.sleep(3*node['number'])
        msg = f"{node['letter']} done!"
        inner_progress.update()
        return msg

def outer_function(**config):
    """Outer function running inner function for each task in input dict"""
    freeze_support()  # for Windows support
    tqdm.set_lock(RLock())

    with concurrent.futures.ThreadPoolExecutor(initializer=tqdm.set_lock,
                            initargs=(tqdm.get_lock(),),max_workers=3) as executor:
        results_list = []
        outer_loop_kwarg = {
            'total': len(config['package']['tasks']),
            'desc': 'Outer',
            'ascii': True,
            'position': len(config['package']['tasks']),
            'leave': True
        }

        with tqdm(**outer_loop_kwarg) as out_progress:
            futuresListComp = [executor.submit(inner_function,**node) for node in config['package']['tasks']]

            # Update after each completed task
            for future in concurrent.futures.as_completed(futuresListComp):
                out_progress.update()
                results_list.append(future.result())

        return results_list

def main():
    dict_of_data = {
        'package':  {
                    'tasks': [
                        {'number': 1,
                         'letter': 'a'},
                        {'number': 2,
                        'letter': 'b'},
                        {'number': 3,
                         'letter': 'c'}
                        ]
                    }
    }

    outer_function(**dict_of_data)

if __name__ == "__main__":
    main()
