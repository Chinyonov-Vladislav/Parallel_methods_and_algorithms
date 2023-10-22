// Task4.cpp : Этот файл содержит функцию "main". Здесь начинается и заканчивается выполнение программы.
//
#include <iostream>
#include <omp.h>
#include <vector>
#include <chrono>
#include <stdexcept>
#include <conio.h>
using namespace std;


void swap(int* a, int* b)
{
    int t = *a;
    *a = *b;
    *b = t;
}
 
int partition(int arr[], int start, int end)
{
    int pivot = arr[end];

    // элементы, меньшие точки поворота, будут перемещены влево от `pIndex`
    // элементы больше, чем точка поворота, будут сдвинуты вправо от `pIndex`
    // равные элементы могут идти в любом направлении
    int pIndex = start;

    // каждый раз, когда мы находим элемент, меньший или равный опорному, `pIndex`
    // увеличивается, и этот элемент будет помещен перед опорной точкой.
    for (int i = start; i < end; i++)
    {
        if (arr[i] <= pivot)
        {
            swap(arr[i], arr[pIndex]);
            pIndex++;
        }
    }

    // поменять местами `pIndex` с пивотом
    swap(arr[pIndex], arr[end]);

    // вернуть `pIndex` (индекс опорного элемента)
    return pIndex;
}
 
void quicksort(int arr[], int start, int end, bool use_OpenMP)
{    
    if (start < end) {
        int pivot = partition(arr, start, end);
        if (use_OpenMP)
        {
            #pragma omp parallel sections
            {
                #pragma omp section
                {
                    //printf("Section 1 id = %d \n", omp_get_thread_num());
                    quicksort(arr, start, pivot - 1, use_OpenMP);
                }
                #pragma omp section
                {
                    //printf("Section 2 id = %d \n", omp_get_thread_num());
                    quicksort(arr, pivot + 1, end, use_OpenMP);
                }
            }
        }
        else
        {
            quicksort(arr, start, pivot - 1, use_OpenMP);
            quicksort(arr, pivot + 1, end, use_OpenMP);
        }
    }

}


int main()
{
    int count_elements_in_array;

    cout << "Enter the number of array elements: ";
    cin >> count_elements_in_array;

    int* arr = new int[count_elements_in_array];
    int choice = -1;
    while (true)
    {
        try
        {
            int temp;
            cout << "Choose the method of filling the array: 1 - manual entry of elements, 2 - automatic filling of the array of numbers in the range from 0 to 100: ";
            cin >> temp;
            if (std::cin.fail() || (temp != 1 && temp != 2))
            {
                throw std::runtime_error("Error when choosing the method of filling the array. Try again!");
            }
            choice = temp;
            break;
        }
        catch (const std::runtime_error& e)
        {
            std::cerr << "Exception: " << e.what() << std::endl;
            std::cin.clear();
            std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
        }
    }
    if (choice == 1)
    {
        for (int i = 0; i < count_elements_in_array; i++) {
            while (true)
            {
                try
                {
                    int temp;
                    cout << "Enter " << i << " array element: ";
                    cin >> temp;
                    if (std::cin.fail())
                    {
                        throw std::runtime_error("Error when entering an array element. Try again!");
                    }
                    arr[i] = temp;
                    break;
                }
                catch (const std::runtime_error& e)
                {
                    std::cerr << "Exception: " << e.what() << std::endl;
                    std::cin.clear();
                    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
                }
            }
        }
    }
    else
    {
        for (int i = 0; i < count_elements_in_array; i++)
        {
            arr[i] = std::rand() % 100 + 1;
        }
    }
    
    int* copy_arr = new int[count_elements_in_array];
    for (int i = 0; i < count_elements_in_array; ++i) {
        copy_arr[i] = arr[i];
    }

    cout << "Array before sorting: ";
    for (int i = 0; i < count_elements_in_array; i++)
    {
        if (i == count_elements_in_array - 1)
        {
            cout << arr[i] << std::endl;
        }
        else
        {
            cout << arr[i] << " ";
        }
    }
    auto start_time = std::chrono::high_resolution_clock::now();
    omp_set_nested(1);
    quicksort(arr, 0, count_elements_in_array - 1,true);
    auto end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> parallel_duration = end_time - start_time;
    start_time = std::chrono::high_resolution_clock::now();
    quicksort(copy_arr, 0, count_elements_in_array - 1, false);
    end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> serial_duration = end_time - start_time;
    // Printing the sorted array
    cout << "Array after sorting: ";

    for (int i = 0; i < count_elements_in_array; i++) {
        if (i == count_elements_in_array - 1)
        {
            cout << arr[i] << std::endl;
        }
        else
        {
            cout << arr[i] << " ";
        }
    }
    std::cout << "Execution time in single-threaded mode: " << serial_duration.count() << " seconds" << std::endl;
    std::cout << "Execution time in parallel mode: " << parallel_duration.count() << " seconds" << std::endl;
    std::cout << "Boost: " << serial_duration.count() / parallel_duration.count() << std::endl;
    delete[] arr;
    delete[] copy_arr;
    getch();
    return 0;
}

// Запуск программы: CTRL+F5 или меню "Отладка" > "Запуск без отладки"
// Отладка программы: F5 или меню "Отладка" > "Запустить отладку"

// Советы по началу работы 
//   1. В окне обозревателя решений можно добавлять файлы и управлять ими.
//   2. В окне Team Explorer можно подключиться к системе управления версиями.
//   3. В окне "Выходные данные" можно просматривать выходные данные сборки и другие сообщения.
//   4. В окне "Список ошибок" можно просматривать ошибки.
//   5. Последовательно выберите пункты меню "Проект" > "Добавить новый элемент", чтобы создать файлы кода, или "Проект" > "Добавить существующий элемент", чтобы добавить в проект существующие файлы кода.
//   6. Чтобы снова открыть этот проект позже, выберите пункты меню "Файл" > "Открыть" > "Проект" и выберите SLN-файл.
