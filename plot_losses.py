import matplotlib.pyplot as plt
import ast

# Read the losses from the text file
with open('all_loss.txt', 'r') as file:
    data = file.read()

# Convert string representation of list to an actual list
losses = ast.literal_eval(data)

# Transpose the list to separate each loss type
transposed_losses = list(map(list, zip(*losses)))

# Plot each loss on a separate graph
for i, loss in enumerate(transposed_losses, 1):
    plt.figure()
    plt.plot(loss, marker='o', linestyle='-', label=f'Loss {i}')
    plt.title(f'Loss {i} Over Epochs')
    plt.xlabel('Epoch')
    plt.ylabel(f'Loss {i}')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'loss_{i}.png')  # Save the plot as an image file
    plt.show()  # Display the plot
