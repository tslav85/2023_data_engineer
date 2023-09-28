-- public.trascheev_project_sb definition

-- Drop table

-- DROP TABLE public.trascheev_project_sb;

CREATE TABLE public.trascheev_project_sb (
	usercode varchar(255) NOT NULL,
	sensorcode varchar(255) NOT NULL,
	"time" timestamp NOT NULL,
	"position" float8 NULL
)
WITH (
	appendonly=true,
	orientation=column
)
DISTRIBUTED RANDOMLY;