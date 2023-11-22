from influxdb_client_3 import InfluxDBClient3
from os import getenv
from time import sleep
from adtk.data import validate_series
from adtk.detector import LevelShiftAD



# InfluxDB 3.0
host = getenv("INFLUX_HOST", "eu-central-1-1.aws.cloud2.influxdata.com")
org = getenv("INFLUX_ORG", "6a841c0c08328fb1")
database = getenv("INFLUX_DATABASE", "factory")
token = getenv("INFLUX_TOKEN", "foo")
interval = getenv("INTERVAL", 10)

client = InfluxDBClient3(
    token=token,
    host=host,
    org=org,
    database=database)

   
Table = client.query(query='''SELECT DISTINCT("machineID") FROM iox.machine_data WHERE time > (NOW() - INTERVAL '5 minutes')''',language="sql", mode="all")

print(Table)
d = Table.to_pydict()
machines = d['machineID']
level_shift_ad = LevelShiftAD(c=4.0, side='both', window=4)

while True:
   for machine in machines:

      try:
         Table = client.query(query=f"SELECT \"machineID\", vibration, time FROM iox.machine_data WHERE time > (NOW() - INTERVAL '5 minutes') AND \"machineID\" = '{machine}'",language="sql", mode="all")

         print(Table)
               # Convert to Pandas DataFrame
         df = Table.to_pandas().set_index("time")
         df_temp = df.drop(columns=["machineID"])

         s_train = validate_series(df_temp)
         anomalies = level_shift_ad.fit_detect(s_train, return_list=False).rename(columns={"vibration": "anomalies"})


         df = df.merge(anomalies, on="time", how="left")
         df["anomalies"] = df["anomalies"].fillna(0).astype(int)
         print(df)

         # Write to InfluxDB
         print("Writing data to InfluxDB...", flush=True)
         client.write(df, data_frame_measurement_name='machine_data_aggregated', data_frame_tag_columns=['machineID'])
         print(f"Sleeping for {interval} ", flush=True)
      except Exception as e:
         print(e)


   sleep(int(interval))


        


