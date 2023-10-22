// Task8.cpp : Этот файл содержит функцию "main". Здесь начинается и заканчивается выполнение программы.
//
#include <omp.h>
#include <cmath>
#include <iostream>
#include <ctime>
#include <cstdlib>
#include <random>
#include <chrono>
#include <stdexcept>
using namespace std;

bool isPointInsideCircle(double x, double y, double radius) {
	return x*x + y*y <= radius*radius;
}



double MonteCarlo(int count_attempts, double radius_circle, bool use_openMP, int count_threads = 1)
{
	int count_points_inside_circle = 0;
	std::random_device rd;
	std::mt19937_64 gen(rd());
	std::uniform_real_distribution<double> distribution(radius_circle * -1, radius_circle);
	if (use_openMP)
	{
		omp_set_num_threads(count_threads);
		#pragma omp parallel for reduction(+:count_points_inside_circle)
		for (int i = 0; i < count_attempts; i++)
		{
			double coord_x = distribution(gen);
			double coord_y = distribution(gen);
			if (isPointInsideCircle(coord_x, coord_y, radius_circle))
			{
				++count_points_inside_circle;
			}
		}
	}
	else
	{
		for (int i = 0; i < count_attempts; i++)
		{
			double coord_x = distribution(gen);
			double coord_y = distribution(gen);
			if (isPointInsideCircle(coord_x, coord_y, radius_circle))
			{
				++count_points_inside_circle;
			}
		}
	}
	return 4.0 * (double)count_points_inside_circle / (double)count_attempts;
}

int main()
{
	int count_attempts;
	double radius_circle;
	int count_threads;
	while (true)
	{
		try
		{
			int temp;
			std::cout << "Enter a value for the variable \"Number of attempts\" (positive integer greater than 0): ";
			std::cin >> temp;
			if (std::cin.fail() || temp <= 0)
			{
				throw std::runtime_error("You entered a non-positive integer");
			}
			count_attempts = temp;
			break;
		}
		catch (const std::runtime_error& e)
		{
			std::cerr << "Input error: " << e.what() << std::endl;
			std::cin.clear();
			std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
		}
	}
	while (true)
	{
		try
		{
			double temp;
			std::cout << "Enter a value for the variable \"Circle radius\" (a real positive number greater than 0): ";
			std::cin >> temp;
			if (std::cin.fail() || temp <= 0)
			{
				throw std::runtime_error("You entered a non-real positive number");
			}
			radius_circle = temp;
			break;
		}
		catch (const std::runtime_error& e)
		{
			std::cerr << "Input error: " << e.what() << std::endl;
			std::cin.clear();
			std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
		}
	}
	while (true)
	{
		try
		{
			int temp;
			std::cout << "Enter a value for the variable \"Number of threads\" (a positive integer greater than 0):";
			std::cin >> temp;
			if (std::cin.fail() || temp <= 0)
			{
				throw std::runtime_error("You entered a non-real positive number");
			}
			count_threads = temp;
			break;
		}
		catch (const std::runtime_error& e)
		{
			std::cerr << "Input Error: " << e.what() << std::endl;
			std::cin.clear();
			std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
		}
	}
	auto start_time = std::chrono::high_resolution_clock::now();
	double pi = MonteCarlo(count_attempts, radius_circle, true, count_threads);
	auto end_time = std::chrono::high_resolution_clock::now();
	std::cout << "The value of PI using the Monte Carlo method (number of iterations = " << count_attempts << ") using the OpenMP library): " << pi << std::endl;
	std::chrono::duration<double> parallel_duration = end_time - start_time;

	start_time = std::chrono::high_resolution_clock::now();
	pi = MonteCarlo(count_attempts, radius_circle, false);
	end_time = std::chrono::high_resolution_clock::now();
	std::cout << "The value of PI using the Monte Carlo method (number of iterations = " << count_attempts << ") without using the OpenMP library): " << pi << std::endl;
	std::chrono::duration<double> serial_duration = end_time - start_time;
	std::cout << "Execution time in single-threaded mode: " << serial_duration.count() << " seconds" << std::endl;
	std::cout << "Execution time in multi-threaded mode: " << parallel_duration.count() << " seconds" << std::endl;
	std::cout << "Boost: " << serial_duration.count() / parallel_duration.count() << std::endl;
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
