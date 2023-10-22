#include <iostream>
#include <chrono>
#include <omp.h>
#include <conio.h>
using namespace std;


void merge(int arr[], int left, int middle, int right) {
     int n1 = middle - left + 1;
     int n2 = right - middle;

     int* L = new int[n1];
     int* R = new int[n2];

    for (int i = 0; i < n1; i++)
        L[i] = arr[left + i];
    for (int j = 0; j < n2; j++)
        R[j] = arr[middle + 1 + j];

    int i = 0;
    int j = 0;
    int k = left;

    while (i < n1 && j < n2) {
        if (L[i] <= R[j]) {
            arr[k] = L[i];
            i++;
        }
        else {
            arr[k] = R[j];
            j++;
        }
        k++;
    }

    while (i < n1) {
        arr[k] = L[i];
        i++;
        k++;
    }

    while (j < n2) {
        arr[k] = R[j];
        j++;
        k++;
    }
    delete[] L;
    delete[] R;
}


void mergesort(int array[], int low, int high, bool use_OpenMP)
{
    int mid;
    if (low < high)
    {
        int mid = low + (high - low) / 2;
        if (use_OpenMP)
        {
            #pragma omp parallel sections
            {
                #pragma omp section
                {
                    //std::cout << "Section 1 ID = " << omp_get_thread_num() << std::endl;
                    mergesort(array, low, mid, use_OpenMP);
                }
                #pragma omp section
                {
                    //std::cout << "Section 2 ID = " << omp_get_thread_num() << std::endl;
                    mergesort(array, mid + 1, high, use_OpenMP);
                }
            }
        }
        else
        {
            mergesort(array, low, mid, use_OpenMP);
            mergesort(array, mid + 1, high, use_OpenMP);
        }
        merge(array, low, mid, high);
    }
}


int main()
{
    int size;
    while (true)
    {
        try
        {
            int temp;
            std::cout << "Enter the number of array elements (positive integer) greater than 0: ";
            cin >> temp;
            if (cin.fail() || temp <= 0)
            {
                throw std::runtime_error("You entered a non-positive integer");
            }
            size = temp;
            break;
        }
        catch (const std::runtime_error& e)
        {
            cerr << "Input Error: " << e.what() << endl;
            cin.clear();
            cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
        }
    }
    int* arr = new int[size];
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
        for (int i = 0; i < size; i++)
        {
            while (true)
            {
                try
                {
                    int temp;
                    std::cout << "Enter " << i << " array element: ";
                    cin >> temp;
                    if (std::cin.fail())
                    {
                        throw std::runtime_error("error when entering an array element. Try again!");
                    }
                    arr[i] = temp;
                    break;
                }
                catch (const std::runtime_error& e)
                {
                    cerr << "Exception: " << e.what() << endl;
                    cin.clear();
                    cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
                }
            }
        }
    }
    else
    {
        for (int i = 0; i < size; i++)
        {
            arr[i] = std::rand() % 100 + 1;
        }
    }
    int* copy_arr = new int[size];
    for (int i = 0; i < size; i++)
    {
        copy_arr[i] = arr[i];
    }
    std::cout << "Array before sorting: ";
    for (int i = 0; i < size; i++)
    {
        if (i == size - 1)
        {
            std::cout << arr[i] << std::endl;
        }
        else
        {
            std::cout << arr[i] << " ";
        }
    }
    omp_set_nested(1);
    auto start_time_omp = std::chrono::high_resolution_clock::now();
    //auto start_time_omp = omp_get_wtime();
    mergesort(arr, 0, size - 1, true);
    auto end_time_omp = std::chrono::high_resolution_clock::now();
    //auto end_time_omp = omp_get_wtime();
    std::chrono::duration<double> parallel_duration = end_time_omp - start_time_omp;
    auto start_time = std::chrono::high_resolution_clock::now();
    mergesort(copy_arr, 0, size - 1, false);
    auto end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> serial_duration = end_time - start_time;
    std::cout << "Array after sorting: ";
    for (int i = 0; i < size; i++) {
        if (i == size-1)
        {
            std::cout << arr[i] << endl;
        }
        else
        {
            std::cout << arr[i] << " ";
        }
    }
    std::cout << "Execution time in single-threaded mode: " << serial_duration.count() << " seconds" << std::endl;
    std::cout << "Execution time in parallel mode: " << parallel_duration.count() << " seconds" << std::endl;
    std::cout << "Boost: " << serial_duration.count() / parallel_duration.count() << std::endl;
    delete[] arr;
    return 0;
}
