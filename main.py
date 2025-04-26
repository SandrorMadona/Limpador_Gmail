import imaplib
import email
from email.header import decode_header

# Credenciais
user_login = input("Insira seu gmail: ")
password = input("Insira sua senha: ")  # A senha pode ser um App Password, se tiver 2FA ativado

# Conexão com o servidor IMAP do Gmail
conection = imaplib.IMAP4_SSL("imap.gmail.com")

# Tente realizar o login e capture exceções
try:
    conection.login(user_login, password)
except imaplib.IMAP4.error as e:
    print(f"Erro ao fazer login: {e}")
    exit()

# Seleciona a pasta INBOX
conection.select("INBOX")

# Pesquisa todos os emails
status, emails = conection.search(None, "ALL")
if status != "OK":
    print("Erro ao buscar emails.")
    conection.close()
    conection.logout()
    exit()

# Lista de emails a serem verificados
mensagens = emails[0].split()

# Pergunta ao usuário as palavras para excluir
input_text = input("Escreva as palavras separadas por espaço que você quer excluir:  ")
text_to_delete = input_text.split()

# Loop para verificar e deletar os emails
for msg_id in mensagens:
    typ, data = conection.fetch(msg_id, "(RFC822)")

    for resposta in data:
        if isinstance(resposta, tuple):
            mensagem = email.message_from_bytes(resposta[1])

            subject = mensagem["Subject"]
            assunto = "(Sem assunto)"  # Inicializa com um valor padrão

            if subject:
                decoded = decode_header(subject)[0]
                assunto, codificacao = decoded

                if isinstance(assunto, bytes):
                    try:
                        if codificacao is None or codificacao.lower() in ["unknown-8bit", "unknown"]:
                            assunto = assunto.decode("utf-8", errors="replace")
                        else:
                            assunto = assunto.decode(codificacao, errors="replace")
                    except LookupError:
                        assunto = assunto.decode("utf-8", errors="replace")

            print(f"Assunto encontrado: {assunto}")

            # Verifica se alguma palavra a ser deletada está no assunto
            assunto_limpo = assunto.strip().lower()
            if any(palavra.lower() in assunto_limpo for palavra in text_to_delete):
                print(f"Deletando: {assunto}")
                conection.store(msg_id, '+FLAGS', '\\Deleted')  # Marca como deletado

# Aplica a exclusão de fato
conection.expunge()

# Encerra a conexão com o servidor IMAP
conection.logout()
