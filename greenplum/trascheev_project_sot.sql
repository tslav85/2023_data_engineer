-- public.trascheev_project_sot definition

-- Drop table

-- DROP TABLE public.trascheev_project_sot;

CREATE TABLE public.trascheev_project_sot (
	usercode varchar(255) NOT NULL,
	sensorcode varchar(255) NOT NULL,
	"time" timestamp NOT NULL,
	temperature float8 NULL
)
WITH (
	appendonly=true,
	orientation=column
)
DISTRIBUTED RANDOMLY;