-- public.trascheev_project_sit definition

-- Drop table

-- DROP TABLE public.trascheev_project_sit;

CREATE TABLE public.trascheev_project_sit (
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