"""
Background Remover Performance Test

A comprehensive performance testing module for background removal operations.
Provides detailed metrics on timing, memory usage, and CPU utilization.
"""

import time
import psutil
import os
import threading
from typing import Dict, Any, Tuple
from PIL import Image
from background_remover import BackgroundRemover


class PerformanceMonitor:
    """Monitors system performance metrics during execution."""
    
    def __init__(self) -> None:
        self.is_monitoring = False
        self.memory_samples = []
        self.cpu_samples = []
        self.timestamps = []
        self.process = psutil.Process(os.getpid())
        self.monitor_thread = None
        
    def start_monitoring(self) -> None:
        """Start performance monitoring in a separate thread."""
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self) -> None:
        """Stop performance monitoring."""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
    
    def _monitoring_loop(self) -> None:
        """Internal monitoring loop that runs in a separate thread."""
        start_time = time.time()
        while self.is_monitoring:
            try:
                current_time = time.time() - start_time
                memory_mb = self.process.memory_info().rss / (1024 * 1024)
                cpu_percent = self.process.cpu_percent()
                
                self.timestamps.append(current_time)
                self.memory_samples.append(memory_mb)
                self.cpu_samples.append(cpu_percent)
                
                time.sleep(0.1)  # Sample every 100ms
            except Exception:
                break
    
    def get_statistics(self) -> Dict[str, float]:
        """Get comprehensive monitoring statistics."""
        if not self.memory_samples:
            return self._empty_stats()
        
        return {
            'peak_memory_mb': max(self.memory_samples),
            'avg_memory_mb': sum(self.memory_samples) / len(self.memory_samples),
            'avg_cpu_percent': sum(self.cpu_samples) / len(self.cpu_samples) if self.cpu_samples else 0,
            'max_cpu_percent': max(self.cpu_samples) if self.cpu_samples else 0,
            'samples_count': len(self.memory_samples),
            'duration_seconds': self.timestamps[-1] if self.timestamps else 0
        }
    
    def _empty_stats(self) -> Dict[str, float]:
        """Return empty statistics when no data is available."""
        return {
            'peak_memory_mb': 0,
            'avg_memory_mb': 0,
            'avg_cpu_percent': 0,
            'max_cpu_percent': 0,
            'samples_count': 0,
            'duration_seconds': 0
        }


class SystemInfo:
    """Provides system information and utilities."""
    
    @staticmethod
    def get_memory_usage_mb() -> float:
        """Get current process memory usage in MB."""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 * 1024)
    
    @staticmethod
    def get_system_specs() -> Dict[str, Any]:
        """Get comprehensive system specifications."""
        cpu_freq = psutil.cpu_freq()
        return {
            'cpu_count': psutil.cpu_count(),
            'cpu_freq_mhz': cpu_freq.current if cpu_freq else 'N/A',
            'total_memory_gb': psutil.virtual_memory().total / (1024 ** 3),
            'available_memory_gb': psutil.virtual_memory().available / (1024 ** 3),
        }
    
    @staticmethod
    def get_file_size_mb(file_path: str) -> float:
        """Get file size in MB."""
        try:
            return os.path.getsize(file_path) / (1024 * 1024)
        except OSError:
            return 0.0


class TimeFormatter:
    """Utility class for time formatting."""
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format time duration in a human-readable format."""
        if seconds < 1:
            return f"{seconds * 1000:.2f} ms"
        elif seconds < 60:
            return f"{seconds:.2f} s"
        else:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds:.2f}s"


class PerformanceReporter:
    """Handles performance reporting and display."""
    
    def __init__(self):
        self.time_formatter = TimeFormatter()
    
    def print_system_info(self, system_specs: Dict[str, Any]) -> None:
        """Print system information header."""
        print("=" * 70)
        print("BACKGROUND REMOVER PERFORMANCE TEST")
        print("=" * 70)
        print("SYSTEM INFORMATION:")
        print(f"  CPU: {system_specs['cpu_count']} cores @ {system_specs['cpu_freq_mhz']} MHz")
        print(f"  Total RAM: {system_specs['total_memory_gb']:.1f} GB")
        print(f"  Available RAM: {system_specs['available_memory_gb']:.1f} GB")
        print("=" * 70)
    
    def print_initialization_results(self, duration: float, memory_before: float, 
                                   memory_after: float, cpu_stats: Dict[str, float]) -> None:
        """Print initialization performance results."""
        print("\nInitializing BackgroundRemover...")
        print(f"Initialization time: {self.time_formatter.format_duration(duration)}")
        print(f"Memory after initialization: {memory_after:.2f} MB")
        print(f"Memory used during initialization: {memory_after - memory_before:.2f} MB")
        print(f"Average CPU during initialization: {cpu_stats['avg_cpu_percent']:.1f}%")
    
    def print_loading_results(self, duration: float, image_size: Tuple[int, int], 
                            image_mode: str, memory_after: float) -> None:
        """Print image loading performance results."""
        print(f"\nImage loading time: {self.time_formatter.format_duration(duration)}")
        print(f"Original image size: {image_size}, mode: {image_mode}")
        print(f"Memory after loading: {memory_after:.2f} MB")
    
    def print_processing_results(self, duration: float, result_size: Tuple[int, int],
                               result_mode: str, memory_after: float, 
                               process_stats: Dict[str, float]) -> None:
        """Print background removal processing results."""
        print(f"\nProcessing time: {self.time_formatter.format_duration(duration)}")
        print(f"Result image size: {result_size}, mode: {result_mode}")
        print(f"Memory after processing: {memory_after:.2f} MB")
        print(f"Peak memory during processing: {process_stats['peak_memory_mb']:.2f} MB")
        print(f"Average memory during processing: {process_stats['avg_memory_mb']:.2f} MB")
        print(f"Average CPU during processing: {process_stats['avg_cpu_percent']:.1f}%")
        print(f"Peak CPU during processing: {process_stats['max_cpu_percent']:.1f}%")
        print(f"Monitoring samples collected: {process_stats['samples_count']} "
              f"({process_stats['samples_count'] * 0.1:.1f}s duration)")
    
    def print_saving_results(self, duration: float, output_path: str, 
                           input_size_mb: float, output_size_mb: float) -> None:
        """Print image saving results."""
        print(f"\nSaving time: {self.time_formatter.format_duration(duration)}")
        print(f"Result saved to: {output_path}")
        print(f"Input file size: {input_size_mb:.2f} MB")
        print(f"Output file size: {output_size_mb:.2f} MB")
    
    def print_performance_summary(self, timing_data: Dict[str, float], 
                                memory_data: Dict[str, float], 
                                cpu_data: Dict[str, float],
                                performance_data: Dict[str, Any]) -> None:
        """Print comprehensive performance summary."""
        total_time = sum(timing_data.values())
        
        print("\n" + "=" * 70)
        print("PERFORMANCE SUMMARY")
        print("=" * 70)
        print(f"Total execution time: {self.time_formatter.format_duration(total_time)}")
        
        # Timing breakdown
        for operation, duration in timing_data.items():
            percentage = (duration / total_time * 100) if total_time > 0 else 0
            formatted_time = self.time_formatter.format_duration(duration)
            print(f"  - {operation.title()}: {formatted_time} ({percentage:.1f}%)")
        
        # Memory statistics
        print(f"\nMemory Statistics:")
        print(f"  - Total memory used: {memory_data['total_used_mb']:.2f} MB")
        print(f"  - Peak memory: {memory_data['peak_mb']:.2f} MB")
        print(f"  - Memory efficiency: {memory_data['efficiency']:.2f} MB processed per GB used")
        
        # CPU statistics
        print(f"\nCPU Statistics:")
        print(f"  - Average CPU usage: {cpu_data['avg_percent']:.1f}%")
        print(f"  - Peak CPU usage: {cpu_data['max_percent']:.1f}%")
        
        # Performance metrics
        print(f"\nPerformance Metrics:")
        print(f"  - Pixels processed: {performance_data['pixels_processed']:,}")
        print(f"  - Processing throughput: {performance_data['pixels_per_second']:,.0f} pixels/sec")
        print("=" * 70)


class BackgroundRemoverTester:
    """Main class for testing background remover performance."""
    
    def __init__(self, image_path: str = "./example.png", output_path: str = "./example_output.png"):
        self.image_path = image_path
        self.output_path = output_path
        self.system_info = SystemInfo()
        self.reporter = PerformanceReporter()
        
    def run_performance_test(self) -> None:
        """Execute the complete performance test suite."""
        try:
            # Display system information
            system_specs = self.system_info.get_system_specs()
            self.reporter.print_system_info(system_specs)
            
            # Track initial memory
            initial_memory = self.system_info.get_memory_usage_mb()
            print(f"Initial process memory: {initial_memory:.2f} MB")
            
            # Test initialization
            bg_remover, init_timing, init_memory, init_cpu_stats = self._test_initialization()
            
            # Test image loading
            image, load_timing, load_memory = self._test_image_loading()
            
            # Test background removal
            result, process_timing, process_memory, process_stats = self._test_background_removal(
                bg_remover, image
            )
            
            # Test image saving
            save_timing, input_size_mb, output_size_mb = self._test_image_saving(result)
            
            # Calculate final metrics
            final_memory = self.system_info.get_memory_usage_mb()
            
            # Display comprehensive summary
            self._display_performance_summary(
                initial_memory, final_memory, init_timing, load_timing, 
                process_timing, save_timing, init_cpu_stats, process_stats,
                image, input_size_mb, output_size_mb
            )
            
        except FileNotFoundError:
            print(f"Test image not found: {self.image_path}")
            print("Please ensure the test image exists in the specified location.")
        except Exception as e:
            print(f"Error during performance test: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _test_initialization(self) -> Tuple[BackgroundRemover, float, float, Dict[str, float]]:
        """Test and measure background remover initialization."""
        monitor = PerformanceMonitor()
        memory_before = self.system_info.get_memory_usage_mb()
        
        monitor.start_monitoring()
        start_time = time.time()
        bg_remover = BackgroundRemover()
        duration = time.time() - start_time
        monitor.stop_monitoring()
        
        memory_after = self.system_info.get_memory_usage_mb()
        cpu_stats = monitor.get_statistics()
        
        self.reporter.print_initialization_results(duration, memory_before, memory_after, cpu_stats)
        
        return bg_remover, duration, memory_after, cpu_stats
    
    def _test_image_loading(self) -> Tuple[Image.Image, float, float]:
        """Test and measure image loading performance."""
        print(f"\nLoading test image: {self.image_path}")
        
        start_time = time.time()
        image = Image.open(self.image_path)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        duration = time.time() - start_time
        
        memory_after = self.system_info.get_memory_usage_mb()
        
        self.reporter.print_loading_results(duration, image.size, image.mode, memory_after)
        
        return image, duration, memory_after
    
    def _test_background_removal(self, bg_remover: BackgroundRemover, 
                               image: Image.Image) -> Tuple[Image.Image, float, float, Dict[str, float]]:
        """Test and measure background removal performance."""
        print("\nRemoving background...")
        
        monitor = PerformanceMonitor()
        monitor.start_monitoring()
        start_time = time.time()
        result = bg_remover.remove_background(image)
        duration = time.time() - start_time
        monitor.stop_monitoring()
        
        memory_after = self.system_info.get_memory_usage_mb()
        process_stats = monitor.get_statistics()
        
        self.reporter.print_processing_results(
            duration, result.size, result.mode, memory_after, process_stats
        )
        
        return result, duration, memory_after, process_stats
    
    def _test_image_saving(self, result: Image.Image) -> Tuple[float, float, float]:
        """Test and measure image saving performance."""
        print("\nSaving result...")
        
        start_time = time.time()
        result.save(self.output_path)
        duration = time.time() - start_time
        
        input_size_mb = self.system_info.get_file_size_mb(self.image_path)
        output_size_mb = self.system_info.get_file_size_mb(self.output_path)
        
        self.reporter.print_saving_results(duration, self.output_path, input_size_mb, output_size_mb)
        
        return duration, input_size_mb, output_size_mb
    
    def _display_performance_summary(self, initial_memory: float, final_memory: float,
                                   init_time: float, load_time: float, process_time: float,
                                   save_time: float, init_cpu_stats: Dict[str, float],
                                   process_stats: Dict[str, float], image: Image.Image,
                                   input_size_mb: float, output_size_mb: float) -> None:
        """Display comprehensive performance summary."""
        timing_data = {
            'initialization': init_time,
            'loading': load_time,
            'processing': process_time,
            'saving': save_time
        }
        
        total_memory_used = final_memory - initial_memory
        memory_data = {
            'total_used_mb': total_memory_used,
            'peak_mb': process_stats['peak_memory_mb'],
            'efficiency': input_size_mb / (total_memory_used / 1024) if total_memory_used > 0 else 0
        }
        
        cpu_data = {
            'avg_percent': process_stats['avg_cpu_percent'],
            'max_percent': process_stats['max_cpu_percent']
        }
        
        pixels_processed = image.size[0] * image.size[1]
        performance_data = {
            'pixels_processed': pixels_processed,
            'pixels_per_second': pixels_processed / process_time if process_time > 0 else 0
        }
        
        self.reporter.print_performance_summary(timing_data, memory_data, cpu_data, performance_data)


def main() -> None:
    """Main entry point for the performance test."""
    tester = BackgroundRemoverTester()
    tester.run_performance_test()


if __name__ == "__main__":
    main()
