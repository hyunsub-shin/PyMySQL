CREATE TABLE IF NOT EXISTS partList (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item VARCHAR(255) NOT NULL,
    partName VARCHAR(255) NOT NULL,
    package VARCHAR(255) NOT NULL,
    qty INT NOT NULL,
    vendor VARCHAR(255) NOT NULL
);

INSERT INTO partList (item, partName, package, qty, vendor) VALUES
    ('resistor', '1k', '1005', 100, 'any'); 