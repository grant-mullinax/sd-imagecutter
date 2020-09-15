def read_label(label):
    split_label = label.split()
    # we can discard the first label, they are all gravestones.
    return (float(split_label[1]), float(split_label[2])), (float(split_label[3]), float(split_label[4]))


def read_labels(filename):
    file = open(filename, "r")
    labels = [read_label(line) for line in open(filename, "r")]
    file.close()
    return labels


if __name__ == '__main__':
    print(read_labels("graves_labels.txt"))
