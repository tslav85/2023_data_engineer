-- public.trascheev_project_see definition

-- Drop table

-- DROP TABLE public.trascheev_project_see;

CREATE TABLE public.trascheev_project_see (
	usercode varchar(255) NOT NULL,
	sensorcode varchar(255) NOT NULL,
	"time" timestamp NOT NULL,
	power float8 NULL
)
WITH (
	appendonly=true,
	orientation=column
)
DISTRIBUTED RANDOMLY;