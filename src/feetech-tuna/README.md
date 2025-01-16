git clone https://github.com/iotdesignshop/Feetech-tuna.git

# 2. Create a virtual environment (Windows)

python -m venv tuna_env
.\tuna_env\Scripts\activate

# 3. Install requirements

pip install -r requirements.txt

# 4. Run the tool (assuming your servo is on COM4)

python tuna.py COM4

> > list # Find all servos
> > select 1 # Select servo ID 1
> > listregs # Show all register values
> > setpos 2000 # Move to position 2000
