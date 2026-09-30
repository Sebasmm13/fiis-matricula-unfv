import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['DATABASE_URL'] = 'postgresql://postgres.byypgkguuyviypwntcav:Morancito132@aws-0-us-west-2.pooler.supabase.com:5432/postgres'
os.environ['DJANGO_SECRET_KEY'] = 'x'
os.environ['DJANGO_DEBUG'] = '1'
django.setup()

from django.db import connection

def get_dbml():
    with connection.cursor() as cursor:
        # Get all tables
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = [row[0] for row in cursor.fetchall()]
        
        dbml_lines = []
        
        for table in tables:
            dbml_lines.append(f"Table {table} {{")
            
            # Get columns
            cursor.execute(f"SELECT column_name, data_type, character_maximum_length, is_nullable FROM information_schema.columns WHERE table_name = '{table}';")
            columns = cursor.fetchall()
            for col in columns:
                col_name = col[0]
                data_type = col[1]
                if col[2]:
                    data_type += f"({col[2]})"
                
                settings = []
                if col[3] == 'NO':
                    settings.append('not null')
                    
                # check if primary key
                cursor.execute(f"SELECT kcu.column_name FROM information_schema.table_constraints tco JOIN information_schema.key_column_usage kcu ON kcu.constraint_name = tco.constraint_name AND kcu.constraint_schema = tco.constraint_schema WHERE tco.constraint_type = 'PRIMARY KEY' AND kcu.table_name = '{table}';")
                pks = [r[0] for r in cursor.fetchall()]
                if col_name in pks:
                    settings.append('pk')
                
                settings_str = f" [{', '.join(settings)}]" if settings else ""
                dbml_lines.append(f"  {col_name} {data_type}{settings_str}")
            
            dbml_lines.append("}\n")
            
        # Get foreign keys
        cursor.execute("""
            SELECT
                tc.table_name, 
                kcu.column_name, 
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name 
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                  AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY';
        """)
        
        fks = cursor.fetchall()
        for fk in fks:
            dbml_lines.append(f"Ref: {fk[0]}.{fk[1]} > {fk[2]}.{fk[3]}")
            
    return "\n".join(dbml_lines)

with open('schema.dbml', 'w', encoding='utf-8') as f:
    f.write(get_dbml())
print("DBML Generated.")
