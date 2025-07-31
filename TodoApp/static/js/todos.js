if (sessionStorage.getItem('todoDeleted') === 'true') {
        alert('Todo deleted successfully');
        sessionStorage.removeItem('todoDeleted'); // Clear the flag
    }