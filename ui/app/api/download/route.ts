// /app/api/download.ts
import fs from 'fs';
import path from 'path';

export async function GET(req: Request, res: Response) {
  
  const { searchParams } = new URL(req.url)
  const id = searchParams.get('fileName')
  //return Response.json(id);

  const fileName: string | string[] = id ?? '';

  if (!fileName || Array.isArray(fileName)) {
    return Response.json('Invalid filename');
  }

  const filePath = path.resolve('agent-volume', fileName);

  if (!fs.existsSync(filePath)) {
    return Response.json('File not found');
  }

  const data = await fs.promises.readFile(filePath);
  return new Response(data, {
    status: 200,
    headers: { 
      'Content-Type': 'application/octet-stream',
      'Content-Disposition': `attachment; filename=${fileName}`,
      'Content-Length': fs.statSync(filePath).size.toString()
    },
  })

}
